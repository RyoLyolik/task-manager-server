import sqlalchemy
from sqlalchemy import event
from sqlalchemy import insert, select, update, delete
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import model
import pandas as pd
from config import DataBaseConfig
import re
from sqlalchemy.exc import *
from sqlalchemy.sql.elements import *


# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# res = pd.read_sql_query("QUERY", engine)

class MainDB:
    def __init__(self):
        engine = create_engine(
            f"postgresql+psycopg2://{DataBaseConfig.user}:{DataBaseConfig.password}@{DataBaseConfig.host}/{DataBaseConfig.dbname}")
        self.conn = engine.connect()

    def insert_user(self, **kwargs):
        transaction = self.conn.begin()
        try:
            query = insert(model.users_table).values(**kwargs).returning(model.users_table.c.user_id)
            insertion = self.conn.execute(query)
            transaction.commit()

            user_id = insertion.first()
            return user_id
        except Exception as e:
            print(e)
            transaction.rollback()

    def insert_task(self, **kwargs):
        transaction = self.conn.begin()
        try:
            query = insert(model.tasks_table).values(**kwargs).returning(model.tasks_table.c.task_id)
            insertion = self.conn.execute(query)
            transaction.commit()

            task_id = insertion.first()
            return task_id
        except Exception as e:
            print(e)
            transaction.rollback()

    def insert_board(self, **kwargs):
        transaction = self.conn.begin()
        try:
            query = insert(model.board_table).values(**kwargs).returning(model.board_table.c.board_id)
            insertion = self.conn.execute(query)
            transaction.commit()

            board_id = insertion.first()
            return board_id
        except Exception as e:
            print(e)
            transaction.rollback()

    def insert_users_boards(self, **kwargs):
        transaction = self.conn.begin()
        try:
            query = insert(model.users_boards).values(**kwargs).returning(model.users_boards.c.user_id,
                                                                          model.users_boards.c.board_id,
                                                                          model.users_boards.c.user_position)
            insertion = self.conn.execute(query)
            transaction.commit()

            user_board = insertion.first()
            return user_board
        except Exception as e:
            print(e)
            transaction.rollback()

    def insert_users_tasks(self, **kwargs):
        transaction = self.conn.begin()
        try:
            query = insert(model.users_tasks).values(**kwargs).returning(model.users_tasks.c.user_id,
                                                                         model.users_tasks.c.task_id,
                                                                         model.users_tasks.c.user_position)
            insertion = self.conn.execute(query)
            transaction.commit()

            user_task = insertion.first()
            return user_task
        except Exception as e:
            print(e)
            transaction.rollback()

    def insert_comment(self, **kwargs):
        transaction = self.conn.begin()
        try:
            query = insert(model.comments).values(**kwargs).returning(model.comments.c.comment_id)
            insertion = self.conn.execute(query)
            transaction.commit()

            comment = insertion.first()
            return comment
        except Exception as e:
            print(e)
            transaction.rollback()

    def insert_file(self, **kwargs):
        transaction = self.conn.begin()
        try:
            query = insert(model.files).values(**kwargs).returning(model.files.c.file_id)
            insertion = self.conn.execute(query)
            transaction.commit()

            file_id = insertion.first()
            return file_id
        except Exception as e:
            print(e)
            transaction.rollback()

    def insert_delete(self, **kwargs):
        transaction = self.conn.begin()
        try:
            query = insert(model.delete_table).values(**kwargs).returning(model.delete_table.c.task_id)
            insertion = self.conn.execute(query)
            transaction.commit()

            task_id = insertion.first()
            return task_id
        except Exception as e:
            print(e)
            transaction.rollback()

    def get_user(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.users_table.c, attr) == kwargs[attr])
            query = select(model.users_table).where(and_(*conditions))
            selection = self.conn.execute(query)
            user = selection.first()
            return user
        except AttributeError as e:
            print(e)

    def get_users(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.users_table.c, attr) == kwargs[attr])
            query = select(model.users_table).where(and_(*conditions))
            selection = self.conn.execute(query)
            user = selection.fetchall()
            return user
        except AttributeError as e:
            print(e)

    def get_user_board(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.users_boards.c, attr) == kwargs[attr])
            query = select(model.users_boards).where(and_(*conditions))
            selection = self.conn.execute(query)
            user = selection.first()
            return user
        except AttributeError as e:
            print(e)

    def get_users_boards(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.users_boards.c, attr) == kwargs[attr])
            query = select(model.users_boards).where(and_(*conditions))
            selection = self.conn.execute(query)
            user = selection.fetchall()
            return user
        except AttributeError as e:
            print(e)

    def get_user_task(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.users_tasks.c, attr) == kwargs[attr])
            query = select(model.users_tasks).where(and_(*conditions))
            selection = self.conn.execute(query)
            user = selection.first()
            return user
        except AttributeError as e:
            print(e)

    def get_users_tasks(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.users_tasks.c, attr) == kwargs[attr])
            query = select(model.users_tasks).where(and_(*conditions))
            selection = self.conn.execute(query)
            user = selection.fetchall()
            return user
        except AttributeError as e:
            print(e)

    def get_board(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.board_table.c, attr) == kwargs[attr])
            query = select(model.board_table).where(and_(*conditions))
            selection = self.conn.execute(query)
            board = selection.first()
            return board
        except AttributeError as e:
            print(e)

    def get_boards(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.board_table.c, attr) == kwargs[attr])
            query = select(model.board_table).where(and_(*conditions))
            selection = self.conn.execute(query)
            board = selection.fetchall()
            return board
        except AttributeError as e:
            print(e)

    def get_comment(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.comments.c, attr) == kwargs[attr])
            query = select(model.comments).where(and_(*conditions))
            selection = self.conn.execute(query)
            user = selection.first()
            return user
        except AttributeError as e:
            print(e)

    def get_comments(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.comments.c, attr) == kwargs[attr])
            query = select(model.comments).where(and_(*conditions))
            selection = self.conn.execute(query)
            user = selection.fetchall()
            return user
        except AttributeError as e:
            print(e)

    def get_task(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.tasks_table.c, attr) == kwargs[attr])
            query = select(model.tasks_table).where(and_(*conditions))
            selection = self.conn.execute(query)
            user = selection.first()
            return user
        except AttributeError as e:
            print(e)

    def get_tasks(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.tasks_table.c, attr) == kwargs[attr])
            query = select(model.tasks_table).where(and_(*conditions))
            selection = self.conn.execute(query)
            tasks = selection.fetchall()
            return tasks
        except AttributeError as e:
            print(e)

    def get_tasks_by_deadline_user_id(self, deadline=None, user_id=None):
        conditions = list()
        try:
            if deadline:
                conditions.append(getattr(model.tasks_table.c, "deadline") <= deadline)
            if user_id:
                conditions.append(getattr(model.tasks_table.c, "user_id") == user_id)
            query = select(model.tasks_table).where(and_(*conditions))
            selection = self.conn.execute(query)
            tasks = selection.fetchall()
            return tasks
        except AttributeError as e:
            print(e)

    def get_file(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.files.c, attr) == kwargs[attr])
            query = select(model.files).where(and_(*conditions))
            selection = self.conn.execute(query)
            file = selection.first()
            return file
        except AttributeError as e:
            print(e)

    def get_files(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.files.c, attr) == kwargs[attr])
            query = select(model.files).where(and_(*conditions))
            selection = self.conn.execute(query)
            file = selection.fetchall()
            return file
        except AttributeError as e:
            print(e)

    def get_delete(self, **kwargs):
        conditions = list()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.delete_table.c, attr) == kwargs[attr])
            query = select(model.delete_table).where(and_(*conditions))
            selection = self.conn.execute(query)
            file = selection.fetchall()
            return file
        except AttributeError as e:
            print(e)

    def update_user(self, where_: dict, values_: dict):
        conditions = list()
        transaction = self.conn.begin()
        try:
            for attr in where_:
                conditions.append(getattr(model.users_table.c, attr) == where_[attr])
            query = update(model.users_table).where(and_(*conditions)).values(**values_)
            self.conn.execute(query)
            transaction.commit()
        except AttributeError as e:
            print(e)
            transaction.rollback()

    def update_board(self, where_: dict, values_: dict):
        conditions = list()
        transaction = self.conn.begin()
        try:
            for attr in where_:
                conditions.append(getattr(model.board_table.c, attr) == where_[attr])
            query = update(model.board_table).where(and_(*conditions)).values(**values_)
            self.conn.execute(query)
            transaction.commit()
        except AttributeError as e:
            print(e)
            transaction.rollback()

    def update_task(self, where_: dict, values_: dict):
        conditions = list()
        transaction = self.conn.begin()
        try:
            for attr in where_:
                conditions.append(getattr(model.tasks_table.c, attr) == where_[attr])
            query = update(model.tasks_table).where(and_(*conditions)).values(**values_)
            self.conn.execute(query)
            transaction.commit()
        except AttributeError as e:
            print(e)
            transaction.rollback()

    def delete_users_boards(self, **kwargs):
        conditions = list()
        transaction = self.conn.begin()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.users_boards.c, attr) == kwargs[attr])
            query = delete(model.users_boards).where(and_(conditions))
            self.conn.execute(query)
            transaction.commit()
        except Exception as e:
            print(e)
            transaction.rollback()

    def delete_users_tasks(self, **kwargs):
        conditions = list()
        transaction = self.conn.begin()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.users_tasks.c, attr) == kwargs[attr])
            query = delete(model.users_tasks).where(and_(conditions))
            self.conn.execute(query)
            transaction.commit()
        except Exception as e:
            print(e)
            transaction.rollback()

    def delete_comment(self, **kwargs):
        conditions = list()
        transaction = self.conn.begin()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.comments.c, attr) == kwargs[attr])
            query = delete(model.comments).where(and_(conditions))
            self.conn.execute(query)
            transaction.commit()
        except Exception as e:
            print(e)
            transaction.rollback()

    def delete_board(self, **kwargs):
        conditions = list()
        transaction = self.conn.begin()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.board_table.c, attr) == kwargs[attr])
            query = delete(model.board_table).where(and_(conditions))
            self.conn.execute(query)
            transaction.commit()
        except Exception as e:
            print(e)
            transaction.rollback()

    def delete_task(self, **kwargs):
        conditions = list()
        transaction = self.conn.begin()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.tasks_table.c, attr) == kwargs[attr])
            query = delete(model.tasks_table).where(and_(conditions))
            self.conn.execute(query)
            transaction.commit()
        except Exception as e:
            print(e)
            transaction.rollback()

    def delete_file(self, **kwargs):
        conditions = list()
        transaction = self.conn.begin()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.files.c, attr) == kwargs[attr])
            query = delete(model.tasks_table).where(and_(conditions))
            self.conn.execute(query)
            transaction.commit()
        except Exception as e:
            print(e)
            transaction.rollback()

    def delete_delete(self, **kwargs):
        conditions = list()
        transaction = self.conn.begin()
        try:
            for attr in kwargs:
                conditions.append(getattr(model.delete_table.c, attr) == kwargs[attr])
            query = delete(model.delete_table).where(and_(conditions))
            self.conn.execute(query)
            transaction.commit()
        except Exception as e:
            print(e)
            transaction.rollback()
