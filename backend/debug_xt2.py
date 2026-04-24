import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()
print(f"=== Shop 4: {shop4.name} ===")
print(f"Token: {shop4.api_token[:50]}...")

client = WBAPIClient(shop4.api_token)

# Try Statistics API (the one that works for Shop 1)
print("\nTrying Statistics API...")
try:
    stats = client.get_products_from_statistics()
    print(f"Statistics API returned: {len(stats)} products")
    if stats:
        print(f"  Sample: {stats[0]}")
    else:
        print("  Empty result - checking raw response...")
        # Let's see what the API actually returns
        import requests
        response = requests.post(
            "https://market-api.wildberries.ru/content/v1/cards/list",
            headers={"Authorization": shop4.api_token},
            json={},
            timeout=30
        )
        print(f"  Raw response status: {response.status_code}")
        print(f"  Raw response: {response.text[:500]}")
except Exception as e:
    print(f"  Error: {e}")

# Try Content API
print("\nTrying Content API...")
try:
    products = client.get_products(limit=5, offset=0, locale="ru")
    print(f"Content API returned: {len(products)} products")
except Exception as e:
    print(f"  Error: {e}")

db.close()
