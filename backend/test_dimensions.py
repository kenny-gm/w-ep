import sys
sys.path.insert(0, '/app/backend')

from app.database import SessionLocal
from app.models.models import Product

db = SessionLocal()

# Check Shop 4 products for dimensions
products = db.query(Product).filter(Product.shop_id == 4).all()
print(f"Shop 4 products: {len(products)}")
for p in products:
    print(f"  nm_id={p.nm_id}, weight={p.weight}, length={p.length}, width={p.width}, height={p.height}")

db.close()
