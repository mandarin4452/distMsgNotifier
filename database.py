import sqlite3


conn = sqlite3.connect('data.db')
cur = conn.cursor()

cur.execute("create table clients (email text primary key, location text);")
cur.execute('select * from clients')
for row in cur:
    print(row)