from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    logs = conn.execute(text("SELECT shop_id, sync_type, status, message, records_count, finished_at FROM sync_logs ORDER BY id DESC LIMIT 10"))
    for l in logs:
        print("%s | Shop %s | %s | %s | %s records | %s" % (l[5], l[0], l[1], l[2], l[4], l[3]))
