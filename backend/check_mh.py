from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info(metric_histories)"))
    for row in result:
        print(row)
