from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    shop = conn.execute(text("SELECT id, name, supplier_id, currency FROM shops WHERE id = 4"))
    for s in shop:
        print("Shop 4: name=%s, supplier_id=%s, currency=%s" % (s[1], s[2], s[3]))
