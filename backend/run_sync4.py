import sys
sys.path.insert(0, '/app/backend')

from app.database import SessionLocal
from app.models.models import Shop
from app.services.sync_fixed import SyncService

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()
print(f"Running sync for Shop 4: {shop4.name}")

sync = SyncService(db, shop4)
result = sync.sync_products(overwrite=True)

print(f"\nSync result: {result}")

db.close()
