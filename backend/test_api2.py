import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 4).first()

print("Testing API for Shop 4: %s" % shop.name)
client = WBAPIClient(shop.api_token)

# Test get_products
products = client.get_products(limit=10, offset=0, locale="ru")
print("get_products returned: %s items" % len(products))

if not products:
    stats_products = client.get_products_from_statistics()
    print("get_products_from_statistics returned: %s items" % len(stats_products))
    if stats_products:
        print("First product sample: %s" % str(stats_products[0])[:200])

db.close()
