# Тут будут функции по работе с бд

import psycopg2
from psycopg2.errors import *
import _sha3

def hashing_password(password, phone):
    hash_ = _sha3.sha3_256((str(password)+str(phone)).encode("utf-8")).hexdigest()
    return hash_

class MainDB:
    def __init__(self, dbname_='Ivnix', user_='postgres', password_='user', host_="localhost"):
        self.conn = psycopg2.connect(
            dbname=dbname_, user=user_,
            password=password_,
            host=host_
        )

    def cursor(self):
        return self.conn.cursor()

    def get_columns(self, tablename):
        cursor = self.cursor()
        cursor.execute(
            "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{}'".format(tablename)
        )
        columns = cursor.fetchall()
        return columns

    def insert(self, tablename, **kwargs):
        cursor = self.cursor()
        query = "INSERT INTO {} ({}) VALUES ({})"
        keys = ", ".join([str(key) for key in kwargs.keys()])
        values = ", ".join(["'" + str(value) + "'" for value in kwargs.values()])
        query = query.format(tablename, keys, values)
        cursor.execute(query=query)
        self.conn.commit()
        cursor.close()
        return 1

    def insert_user(self, phone, password):
        cursor = self.cursor()
        answer = "ok"
        CHECK = self.get_user(phone)
        password_hash = hashing_password(password,phone)
        if not CHECK:
            cursor.execute(
                """
                INSERT INTO USERS (phone_number, password) VALUES (%s, %s) 
                """,
                (phone, password_hash,)
            )
            self.conn.commit()
        else:
            answer = "User already exists"
            self.cursor().close()
            return answer
        return answer

    def get_user(self, phone=None, ID=None):
        cursor = self.cursor()
        if phone:
            cursor.execute(
                """
                SELECT * FROM users WHERE phone_number=%s
                """,
                (phone,)
            )
        if ID:
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

    def __del__(self):
        self.conn.close()
