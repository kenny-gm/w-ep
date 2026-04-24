import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()

for shop_id in [1, 2, 3, 4]:
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        continue
    
    print(f"\n=== Shop {shop_id}: {shop.name} ===")
    client = WBAPIClient(shop.api_token)
    
    # Content API
    cards = client.get_products(limit=100, offset=0, locale="ru")
    print(f"Content API: {len(cards)} products")
    
    # Statistics API (Stocks)
    stocks = client.get_products_from_statistics()
    print(f"Statistics API (stocks): {len(stocks)} products")
    
    # Check if products exist in DB
    from app.models.models import Product
    db_prods = db.query(Product).filter(Product.shop_id == shop_id).count()
    print(f"Products in DB: {db_prods}")

db.close()
