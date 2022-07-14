# ЭТО СТАРАЯ ВЕРСИЯ СЕРВЕРЕА НОВАЯ НАЗЫВАЕТСЯ server.py

import psycopg2
from psycopg2.errors import *  # TODO: на будущее, чтобы разобраться с ошибками в бд( нужно как-то отменять запись)
from ADDITIONAL import hashing_password
from config import DataBaseConfig
import re


class MainDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=DataBaseConfig.dbname,
            user=DataBaseConfig.user,
            password=DataBaseConfig.password,
            host=DataBaseConfig.host
        )  # connect to DB

    def cursor(self):
        return self.conn.cursor()

    def insert_user(self, phone, password):
        cursor = self.cursor()
        cursor.execute(
            """
            INSERT INTO USERS (phone_number, password) VALUES (%s, %s) RETURNING user_id
            """,
            (phone, password,)
        )
        u_id = cursor.fetchone()[0]
        self.conn.commit()
        self.cursor().close()
        return u_id

    def get_user(self, phone=None, ID=None):
        cursor = self.cursor()
        if phone is not None:
            cursor.execute(
                """
                SELECT * FROM users WHERE phone_number=%s
                """,
                (phone,)
            )
        elif ID is not None:
            cursor.execute(
                """
                SELECT * FROM users WHERE user_id=%s
                """,
                (ID,)
            )
        user = cursor.fetchone()
        cursor.close()
        return user

    def insert_board(self, name, color, deadline, description):
        cursor = self.cursor()
        cursor.execute(
            """
            INSERT INTO board (name, color, deadline, description) VALUES(%s,%s,%s, %s) RETURNING board_id
            """, (name, color, deadline, description,)
        )
        b_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return b_id

    def insert_users_boards(self, user_id, board_id, user_position=None):
        if self.get_user(ID=user_id):
            cursor = self.cursor()
            cursor.execute(
                """INSERT INTO users_boards (user_id, board_id, user_position) VALUES (%s, %s, %s)""",
                (user_id, board_id, user_position,)
            )
            self.conn.commit()
            cursor.close()

    def get_boards_by_user(self, user_id):
        cursor = self.cursor()
        cursor.execute(
            """SELECT board_id FROM users_boards WHERE user_id = {}""".format(user_id)
        )
        boards = list(map(lambda x: x[0], cursor.fetchall()))
        cursor.close()
        return boards

    def get_users_boards_by_user_board(self, user_id, board_id):
        cursor = self.cursor()
        cursor.execute(
            """
            SELECT * FROM users_boards WHERE (user_id,board_id) = (%s, %s) 
            """,
            (user_id, board_id,)
        )
        boards_users = cursor.fetchall()
        cursor.close()
        return boards_users

    def get_board(self, board_id):
        cursor = self.cursor()
        cursor.execute(
            """
            SELECT * FROM board WHERE board_id = {}
            """.format(board_id)
        )
        board = cursor.fetchone()
        cursor.close()
        return board

    def insert_task(self, name, board_id, description, deadline):
        cursor = self.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (name, board_id, description, deadline) VALUES(%s,%s,%s,%s) RETURNING task_id
            """, (name, board_id, description, deadline,)
        )
        t_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return t_id

    def get_task(self, task_id):
        cursor = self.cursor()
        cursor.execute(
            """
            SELECT * FROM tasks WHERE task_id=%s
            """, (task_id,)
        )

    def insert_users_tasks(self, task_id, user_id, position):
        if self.get_user(ID=user_id):
            cursor = self.cursor()
            cursor.execute(
                """INSERT INTO users_tasks (user_id, task_id, user_position) VALUES (%s, %s, %s)""",
                (user_id, task_id, position)
            )
            self.conn.commit()
            cursor.close()

    def get_tasks_by_board(self, board_id):
        if self.get_board(board_id):
            cursor = self.cursor()
            cursor.execute(
                """
                SELECT * FROM tasks WHERE board_id = %s
                """,
                (board_id,)
            )
            tasks = cursor.fetchall()
            cursor.close()
            return tasks


    def get_users_tasks(self, task_id=None, user_id=None):
        if task_id and user_id:
            cursor = self.cursor()
            cursor.execute(
                """
                SELECT * FROM users_tasks WHERE (task_id, user_id) = (%s,%s)
                """,
                (task_id, user_id,)
            )
            user_task = cursor.fetchall()
            cursor.close()
            return user_task
        if task_id:
            cursor = self.cursor()
            cursor.execute(
                """
                SELECT * FROM users_tasks WHERE task_id=%s
                """,
                (task_id,)
            )
            task_info = cursor.fetchall()
            cursor.close()
            return task_info

    def update_board(self, board_id,
                     new_name=None,
                     new_deadline=None,
                     new_color=None,
                     new_description=None,
                     new_user_id=None,
                     new_user_position=None,
                     delete_user=None):
        if board_id:
            cursor = self.cursor()
            query =  """
            UPDATE board
            SET {}
            WHERE board_id = %s
            """
            if new_name:
                cursor.execute(
                    query.format("name=%s"),
                    (new_name,board_id,)
                )
            if new_deadline:
                cursor.execute(
                    query.format("deadline=%s"),
                    (new_deadline, board_id,)
                )
            if new_color:
                cursor.execute(
                    query.format("color=%s"),
                    (new_color, board_id,)
                )
            if new_description:
                cursor.execute(
                    query.format("description=%s"),
                    (new_description, board_id,)
                )
            if new_user_id:
                self.insert_users_boards(user_id=new_user_id, board_id=board_id, user_position=new_user_position)
            if delete_user:
                cursor.execute(
                    """
                    DELETE FROM users_boards WHERE user_id=%s
                    """,
                    (delete_user,)
                )
            self.conn.commit()

    def update_task(self, task_id,
                    new_name=None,
                    new_deadline=None,
                    new_performer=None,
                    new_supervisor=None,
                    new_description=None,
                    new_stage=None):
        if task_id:
            cursor = self.cursor()
            query="""
            UPDATE tasks
            SET {}
            WHERE task_id=%s
            """
            if new_name:
                cursor.execute(query.format("name=%s"),
                               (new_name,))
            if new_deadline:
                cursor.execute(query.format("deadline=%s"),
                               (new_deadline,))
            if new_stage:
                cursor.execute(query.format("stage"),
                               (new_stage,))
            if new_description:
                cursor.execute(query.format("description=%s"),
                               (new_description,))

            if new_performer:
                self.insert_users_tasks(task_id=task_id, user_id=new_performer, position="performer")
            if new_supervisor:
                self.insert_users_tasks(task_id=task_id, user_id=new_supervisor, position="supervisor")
            self.conn.commit()

    def insert_comment(self, task_id, author_id, content, date_time):
        if (task_id and author_id and content and date_time):
            cursor = self.cursor()
            cursor.execute(
                """
                INSERT INTO comments (task_id, content, date_time, author_id) = (%s,%s,%s,%s) RETURNING comment_id
                """,
                (task_id, content, date_time, author_id,)
            )
            cursor.fetchone()
            return cursor

    def update_user(self, user_id,
                    new_name=None,
                    new_phone=None,
                    new_password=None,
                    new_email=None,
                    new_telegram=None):
        cursor = self.cursor()
        query = """
        UPDATE users
        SET {}
        WHERE user_id=%s
        """
        if new_name:
            cursor.execute(query.format("name=%s"),
                           (new_name,))
        if new_phone:
            try:
                cursor.execute(query.format("phone_number=%s"),
                               (new_phone,))
            except (Exception):
                self.conn.rollback()

        if new_password:
            cursor.execute(query.format("password=%s"),
                           (new_password,))

        if new_email:
            try:
                cursor.execute(query.format("email=%s"),
                               (new_email,))
            except (Exception):
                self.conn.rollback()

        if new_telegram:
            try:
                cursor.execute(query.format("telegram_id=%s"),
                               (new_telegram,))
            except (Exception):
                self.conn.rollback()
        cursor.close()
        self.conn.commit()

    def delete_users_tasks(self, user_id=None, task_id=None, position=None):
        if user_id and task_id and position:
            cursor = self.cursor()
            cursor.execute(
                """
                DELETE FROM users_tasks WHERE (user_id, task_id, position) = (%s,%s,%s)
                """,
                (user_id,task_id,position,)
            )
            self.conn.commit()
            cursor.close()
        elif task_id:
            cursor = self.cursor()
            cursor.execute(
                """
                DELETE FROM users_tasks WHERE task_id = %s
                """,
                (task_id,)
            )
            self.conn.commit()
            cursor.close()

    def get_comment(self, comment_id):
        cursor = self.cursor()
        cursor.execute(
            """
            SELECT * 
            FROM comments 
            WHERE comment_id=%s
            """,
            (comment_id,)
        )
        comment = cursor.fetchone()
        cursor.close()
        return comment

    def get_comments(self, task_id):
        cursor = self.cursor()
        cursor.execute(
            """
            SELECT * 
            FROM comments 
            WHERE task_id=%s
            """,
            (task_id,)
        )
        comment = cursor.fetchall()
        cursor.close()
        return comment

    def delete_comment(self, comment_id):
        cursor = self.cursor()
        cursor.execute(
            """
            DELETE FROM comments WHERE comment_id=%s
            """,
            (comment_id,)
        )
        self.conn.commit()
        cursor.close()

    def delete_board(self, board_id):
        cursor = self.cursor()
        cursor.execute(
            """
            DELETE
            FROM board
            WHERE board_id=%s
            """,
            (board_id,)
        )
        self.conn.commit()
        cursor.close()

    def delete_task(self, task_id):
        cursor = self.cursor()
        cursor.execute(
            """
            DELETE
            FROM tasks
            WHERE task_id=%s
            """,
            (task_id,)
        )
        self.conn.commit()
        cursor.close()

    def delete_users_boards(self, board_id=None, user_id=None):
        if board_id:
            cursor = self.cursor()
            cursor.execute(
                """
                DELETE
                FROM users_boards
                WHERE board_id=%s
                """,
                (board_id,)
            )

    def custom_query(self, fnc):
        cursor = self.cursor()
        X = fnc(cursor)
        return X

    ################# EXAMPLE FOR REUSABLE FUNCTION ######################
    # def run_custom_query():
    #     @DB.custom_query
    #     def foo(cursor):
    #         cursor.execute(
    #             """SELECT * from USERS WHERE user_id = 13"""
    #         )
    #         x = cursor.fetchone()
    #         return x
    #
    #     return foo
    #
    # print(run_custom_query()) -> [user_id, user_name, ... ]
    ######################################################################

    def __del__(self):
        self.conn.close()
