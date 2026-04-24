from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    prods = conn.execute(text("SELECT id, shop_id, name, nm_id FROM products WHERE shop_id = 4 LIMIT 10"))
    print("Products for shop 4:")
    for p in prods:
        print("  id=%s, shop=%s, name=%s, nm_id=%s" % (p[0], p[1], p[2], p[3]))
