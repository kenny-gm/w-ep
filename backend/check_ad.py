import sqlite3
conn = sqlite3.connect('/app/db/wb_erp.db')
cur = conn.cursor()

# Find product XDJ803-CMH
cur.execute("SELECT id, nm_id, name FROM products WHERE name LIKE '%XDJ803-CMH%'")
print('Product:', cur.fetchone())

# Get ad cost for this product on 04-14
cur.execute("SELECT SUM(cost), SUM(clicks), SUM(order_count) FROM ad_records WHERE product_id=8 AND DATE(record_date)='2026-04-14' AND ad_type='advertising'")
print('Ad cost 04-14:', cur.fetchone())

# Check all dates for this product
cur.execute("SELECT DATE(record_date), cost, clicks, order_count FROM ad_records WHERE product_id=8 AND ad_type='advertising' ORDER BY record_date DESC LIMIT 10")
for r in cur.fetchall():
    print(r)

conn.close()
