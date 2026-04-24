from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    shops = conn.execute(text("SELECT id, name, platform FROM shops LIMIT 5"))
    for s in shops:
        print("Shop %s: %s | platform=%s" % (s[0], s[1], s[2]))
