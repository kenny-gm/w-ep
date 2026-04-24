from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    cols = conn.execute(text("PRAGMA table_info(shops)"))
    print("Shops table columns:")
    for c in cols:
        print("  %s %s" % (c[1], c[2]))
