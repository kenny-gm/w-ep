import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()

for shop_id in [1, 4]:
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    print("\n=== Shop %s: %s ===" % (shop_id, shop.name))
    client = WBAPIClient(shop.api_token)
    
    products = client.get_products(limit=5, offset=0, locale="ru")
    print("get_products: %s items" % len(products))
    
    if not products:
        stats = client.get_products_from_statistics()
        print("get_products_from_statistics: %s items" % len(stats))

db.close()
