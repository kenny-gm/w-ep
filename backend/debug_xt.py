import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()

for shop_id in [1, 4]:
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    print(f"\n=== Shop {shop_id}: {shop.name} ===")
    print(f"Currency: {shop.currency}")
    print(f"Token prefix: {shop.api_token[:30]}...")
    
    client = WBAPIClient(shop.api_token)
    
    # Test Content API
    products = client.get_products(limit=5, offset=0, locale="ru")
    print(f"Content API: {len(products)} products")
    
    # Test Statistics API
    stats = client.get_products_from_statistics()
    print(f"Statistics API: {len(stats)} products")
    if stats:
        print(f"  First product: {stats[0]}")
    
    # Test orders
    orders = client.get_new_orders(limit=10)
    print(f"New orders: {len(orders)}")
    
    # Test campaigns
    campaigns = client.get_advertising_campaigns()
    print(f"Campaigns: {len(campaigns)}")

db.close()
