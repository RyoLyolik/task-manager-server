"""
Data structures, used in project.

You may do changes in tables here, then execute
`alembic revision --message="Your text" --autogenerate`
and alembic would generate new migration for you
in staff/alembic/versions folder.
"""

import sqlalchemy
from sqlalchemy import (
    Column, Enum, Integer, MetaData, SmallInteger, String, Table, ARRAY, Date, Time, DateTime, Boolean, ForeignKey, Constraint, PrimaryKeyConstraint
)

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Default naming convention for all indexes and constraints
# See why this is important and how it would save your time:
# https://alembic.sqlalchemy.org/en/latest/naming.html
convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': (
        'fk__%(table_name)s__%(all_column_names)s__'
        '%(referred_table_name)s'
    ),
    'pk': 'pk__%(table_name)s'
}

# Registry for all tables

metadata = MetaData(naming_convention=convention)

users_table = Table(
    'users',
    metadata,
    Column('user_id', Integer, primary_key=True, autoincrement='auto'),
    Column('username', String(collation='ru-RU-x-icu'), unique=True),
    Column('phone_number', String(16), unique=True, nullable=False),
    Column('password', String(256), nullable=False),
    Column('email', String(256), unique=True),
    Column('telegram_id', Integer, unique=True)
)
board_table = Table(
    'board',
    metadata,
    Column('board_id', Integer, primary_key=True, autoincrement='auto'),
    Column('boardname', String(length=64, collation='ru-RU-x-icu'), nullable=False),
    Column('deadline', Date),
    Column('color', String),  # Hex value
    Column('description', String(collation='ru-RU-x-icu'), nullable=True)
)

tasks_table = Table(
    'tasks',
    metadata,
    Column('task_id', Integer, primary_key=True, autoincrement='auto'),
    Column('taskname', String(length=64, collation='ru-RU-x-icu'), nullable=False),
    Column('board_id', ForeignKey('board.board_id'), nullable=False),
    Column('description', String(collation='ru-RU-x-icu'), nullable=True),
    Column('deadline', Date, nullable=True),
    Column('stage', Integer, default=1),
    Column('author_id', ForeignKey('users.user_id'))
)

delete_table = Table(
    "delete",
    metadata,
    Column('task_id', Integer, unique=True),
    Column('taskname', String(length=64, collation='ru-RU-x-icu'), nullable=False),
    Column('board_id', ForeignKey('board.board_id'), nullable=False),
    Column('description', String(collation='ru-RU-x-icu'), nullable=True),
    Column('deadline', Date, nullable=True),
    Column('stage', Integer, default=0),
    Column('author_id', ForeignKey('users.user_id')),
    PrimaryKeyConstraint('task_id')
)

users_tasks = Table(
    'users_tasks',
    metadata,
    Column('user_id', ForeignKey("users.user_id")),
    Column('task_id', ForeignKey("tasks.task_id")),
    Column('user_position', String),
    PrimaryKeyConstraint('user_id', 'task_id')
)

users_deletedtasks = Table(
    'users_deletedtasks',
    metadata,
    Column('user_id', ForeignKey("users.user_id")),
    Column('task_id', ForeignKey("delete.task_id")),
    Column('user_position', String)
)

users_boards = Table(
    'users_boards',
    metadata,
    Column('user_id', ForeignKey("users.user_id")),
    Column("board_id", ForeignKey("board.board_id")),
    Column("user_position", String, nullable=False, default="user"),
    PrimaryKeyConstraint('user_id', 'board_id')
)

files = Table(
    "files",
    metadata,
    Column('file_id', Integer, primary_key=True,autoincrement='auto'),
    Column('filename', String(250), nullable=False),
    Column('task_id', ForeignKey("tasks.task_id")),
    Column('author_id', ForeignKey("users.user_id"))
)

comments = Table(
    "comments",
    metadata,
    Column('comment_id', Integer, primary_key=True),
    Column('task_id', ForeignKey('tasks.task_id')),
    Column('board_id', ForeignKey('board.board_id')),
    Column('content', String(250), nullable=False),
    Column('author_id', ForeignKey("users.user_id")),
    Column('date_time', DateTime)
)

