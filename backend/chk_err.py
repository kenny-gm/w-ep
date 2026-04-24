from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    logs = conn.execute(text("SELECT message, created_at FROM sync_logs WHERE shop_id = 4 AND status = 'failed' ORDER BY id DESC LIMIT 5"))
    print("Failed syncs for shop 4:")
    for l in logs:
        print("  %s: %s" % (l[1], l[0]))
