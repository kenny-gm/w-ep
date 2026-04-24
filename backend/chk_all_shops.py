from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    shops = conn.execute(text("SELECT id, name, currency, exchange_rate, platform, sync_enabled FROM shops ORDER BY id"))
    print("All shops:")
    for s in shops:
        print("  Shop %s: %s | currency=%s | rate=%s | platform=%s | sync=%s" % (s[0], s[1], s[2], s[3], s[4], s[5]))
