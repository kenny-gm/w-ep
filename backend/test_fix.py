import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()

for shop_id in [1, 4]:
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    print(f"\n=== Shop {shop_id}: {shop.name} ===")
    client = WBAPIClient(shop.api_token)
    products = client.get_products(limit=100, offset=0, locale="ru")
    print(f"Products: {len(products)}")
    if products:
        print(f"First product: nmID={products[0].get('nmID')}, vendorCode={products[0].get('vendorCode')}")

db.close()
