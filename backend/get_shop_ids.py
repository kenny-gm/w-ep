import sys
sys.path.insert(0, '/app')
import logging
logging.disable(logging.CRITICAL)
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT id FROM shops WHERE is_active = 1 AND sync_enabled = 1'))
    ids = [str(row[0]) for row in result]
    print(' '.join(ids))
