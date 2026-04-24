import sys
sys.path.insert(0, '/app/backend')

from app.database import SessionLocal
from app.models.models import Shop
import httpx

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()

# Test with exactly the format from the example
print("=== Test 1: exact format from example ===")
try:
    resp = httpx.post(
        "https://content-api.wildberries.ru/content/v2/get/cards/list?locale=ru",
        headers={"Authorization": shop4.api_token, "Content-Type": "application/json"},
        json={
            "settings": {
                "sort": {"ascending": False},
                "filter": {"withPhoto": -1},
                "cursor": {"limit": 100}
            }
        },
        timeout=30
    )
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test with cursor
print("\n=== Test 2: using cursor with nmID and limit ===")
try:
    resp = httpx.post(
        "https://content-api.wildberries.ru/content/v2/get/cards/list?locale=ru",
        headers={"Authorization": shop4.api_token, "Content-Type": "application/json"},
        json={
            "settings": {
                "cursor": {"limit": 100}
            }
        },
        timeout=30
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Cards: {len(data.get('cards', []))}")
    print(f"Cursor: {data.get('cursor')}")
except Exception as e:
    print(f"Error: {e}")

db.close()
