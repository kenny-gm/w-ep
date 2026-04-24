import sqlite3
conn = sqlite3.connect("/app/db/wb_erp.db")
c = conn.cursor()

c.execute("SELECT id, name, custom_name, shop_id FROM products LIMIT 5")
rows = c.fetchall()
print("Products in DB:")
for row in rows:
    print(f"  id={row[0]}, name={row[1]}, custom_name={row[2]}, shop_id={row[3]}")

conn.close()
