import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop
import httpx

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()

print("=== Testing different Content API versions ===")

# Try v1
print("\n--- v1 POST /content/v1/cards/list ---")
try:
    resp = httpx.post(
        "https://market-api.wildberries.ru/content/v1/cards/list",
        headers={"Authorization": shop4.api_token, "Content-Type": "application/json"},
        json={},
        timeout=30
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Keys: {list(data.keys())}")
    if "data" in data:
        cards = data.get("data", {}).get("cards", [])
        print(f"Cards count: {len(cards)}")
        for card in cards[:2]:
            print(f"  {card}")
except Exception as e:
    print(f"Error: {e}")

# Try v2 with different params
print("\n--- v2 with different params ---")
try:
    resp = httpx.post(
        "https://content-api.wildberries.ru/content/v2/get/cards/list",
        headers={"Authorization": shop4.api_token, "Content-Type": "application/json"},
        json={"limit": 100, "offset": 0, "locale": "en"},
        timeout=30
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Cards: {len(data.get('cards', []))}")
except Exception as e:
    print(f"Error: {e}")

db.close()
