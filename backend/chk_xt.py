from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    # Products
    prods = conn.execute(text("SELECT id, nm_id, name, shop_id FROM products WHERE shop_id = 4"))
    print("=== Products for Shop 4 ===")
    for p in prods:
        print(f"  id={p[0]}, nm_id={p[1]}, name={p[2]}")
    
    # Recent sync logs
    logs = conn.execute(text("SELECT shop_id, sync_type, status, message, finished_at FROM sync_logs WHERE shop_id = 4 ORDER BY id DESC LIMIT 6"))
    print("\n=== Recent Sync Logs for Shop 4 ===")
    for l in logs:
        print(f"  {l[5]} | {l[1]} | {l[2]} | {l[3]}")
