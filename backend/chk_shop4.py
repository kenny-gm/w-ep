from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    shop = conn.execute(text("SELECT id, name, api_token, currency FROM shops WHERE id = 4"))
    for s in shop:
        print("Shop 4: name=%s, currency=%s, token=%s" % (s[1], s[3], s[2][:20] if s[2] else 'None'))
