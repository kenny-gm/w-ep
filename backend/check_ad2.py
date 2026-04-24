from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info(ad_records)"))
    for row in result:
        print(row[1], row[2])
