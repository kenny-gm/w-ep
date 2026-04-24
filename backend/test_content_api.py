import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()
client = WBAPIClient(shop4.api_token)

print("=== Testing Content API v2 ===")

# Try the exact endpoint from documentation
try:
    import httpx
    resp = httpx.post(
        "https://content-api.wildberries.ru/content/v2/get/cards/list",
        headers={"Authorization": shop4.api_token, "Content-Type": "application/json"},
        json={"limit": 100, "offset": 0},
        timeout=30
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Response keys: {list(data.keys())}")
    if "cards" in data:
        print(f"Cards count: {len(data.get('cards', []))}")
        for card in data.get("cards", [])[:3]:
            print(f"  {card}")
    else:
        print(f"Full response: {str(data)[:500]}")
except Exception as e:
    print(f"Error: {e}")

db.close()
