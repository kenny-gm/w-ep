import sqlite3
conn = sqlite3.connect('/app/db/wb_erp.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
for t in tables:
    print(t[0])
