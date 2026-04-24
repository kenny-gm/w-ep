from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    shops = conn.execute(text("SELECT id, name, currency FROM shops ORDER BY id"))
    for s in shops:
        print("Shop %s: %s (%s)" % (s[0], s[1], s[2]))
