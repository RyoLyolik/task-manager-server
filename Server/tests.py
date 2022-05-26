import db
DB = db.MainDB()
from uuid import *
from datetime import datetime
now = datetime.now()
formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
x = DB.insert_board("123", "123", formatted_date, "123")

print(x)