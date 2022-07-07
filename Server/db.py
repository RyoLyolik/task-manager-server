# Тут будут функции по работе с бд

import psycopg2
from psycopg2.errors import *  # TODO: на будущее, чтобы разобраться с ошибками в бд( нужно как-то отменять запись)
from ADDITIONAL import hashing_password
from config import DataBaseConfig


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
        password_hash = hashing_password(password, phone)  # getting hash of password
        cursor.execute(
            """
            INSERT INTO USERS (phone_number, password) VALUES (%s, %s) RETURNING user_id
            """,
            (phone, password_hash,)
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

    def insert_users_boards(self, user_id, board_id):
        if self.get_user(ID=user_id):
            cursor = self.cursor()
            cursor.execute(
                """INSERT INTO users_boards (user_id, board_id) VALUES (%s, %s)""",
                (user_id, board_id)
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
                """INSERT INTO users_boards (user_id, task_id, user_position) VALUES (%s, %s, %s)""",
                (user_id, task_id, position)
            )
            self.conn.commit()
            cursor.close()

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
