import db
DB = db.MainDB()

x = DB.insert('users', name="NAaME", password="PAaSSWORD", email="EMAaILl", telegram_id=1)
# x = ', '.join(['s'])
print(x)