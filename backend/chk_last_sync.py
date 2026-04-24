from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    logs = conn.execute(text("SELECT shop_id, sync_type, finished_at, status, message FROM sync_logs ORDER BY id DESC LIMIT 20"))
    for l in logs:
        print("Shop %s | %s | %s | %s | %s" % (l[0], l[1], l[2], l[3], l[4]))
