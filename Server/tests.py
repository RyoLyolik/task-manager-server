import db

DB = db.MainDB()
from uuid import *
from datetime import datetime
from _sha256 import *
from _sha3 import *

now = datetime.now()
import filecontrol


# FC = filecontrol.FileControl()
# FC.get_file("INITIAL_UPLOAD.py")
# # formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
# # x = DB.insert_board("123", "123", formatted_date, "123")
# #
# # print(x)
#
# print("eqwe123fa".encode("utf-8"))
# x = sha3_256("eqwe2123fa".encode("utf-8")).hexdigest()
# # y = sha256("eqwe2123fa".encode("utf-8")).digest()
# print(x)

def run_custom_query():
    @DB.custom_query
    def foo(cursor):
        cursor.execute(
            """SELECT * from USERS WHERE user_id = 13"""
        )
        x = cursor.fetchone()
        return x

    return foo


print(run_custom_query())
