import sys
sys.path.insert(0, '/app/backend')

from app.database import SessionLocal
from app.models.models import Shop, Product
from app.services.sync_fixed import SyncService

db = SessionLocal()

# Get Shop 4
shop4 = db.query(Shop).filter(Shop.id == 4).first()
print(f"Shop: {shop4.name}")

# Create sync service
sync = SyncService(shop=shop4, db=db)
result = sync.sync_products(limit=100, overwrite=True)
print(f"Sync result: {result}")

# Verify dimensions
prods = db.query(Product).filter(Product.shop_id == 4).all()
print(f"\nShop 4 products after re-sync:")
for p in prods:
    print(f"  {p.nm_id}: weight={p.weight}, length={p.length}, width={p.width}, height={p.height}")

db.close()
