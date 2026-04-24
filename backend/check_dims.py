import sys
sys.path.insert(0, '/app/backend')

from app.database import SessionLocal
from app.models.models import Product

db = SessionLocal()

for shop_id in [1, 2, 3, 4]:
    products = db.query(Product).filter(Product.shop_id == shop_id).all()
    missing = [p for p in products if p.weight is None]
    print(f"Shop {shop_id}: total={len(products)}, missing weight={len(missing)}")
    if missing:
        for p in missing[:5]:
            print(f"  nm_id={p.nm_id}, name={p.name[:20]}, weight={p.weight}")

db.close()
