# Тут будут функции по работе с бд

import psycopg2


class MainDB:
    def __init__(self, dbname_='Ivnix', user_='postgres', password_='user', host_="localhost"):
        self.conn = psycopg2.connect(dbname=dbname_, user=user_, password=password_, host=host_)

    def cursor(self):
        return self.conn.cursor()

    def insert(self, tablename, **kwargs):
        cursor_ = self.cursor()
        query = "INSERT INTO {} ({}) VALUES ({})"
        keys = ", ".join([str(key) for key in kwargs.keys()])
        values = ", ".join(["'"+str(value)+"'" for value in kwargs.values()])
        query = query.format(tablename, keys, values)
        cursor_.execute(query=query)
        self.conn.commit()
        cursor_.close()
        return query


    def __del__(self):
        self.conn.close()