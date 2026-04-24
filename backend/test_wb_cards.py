import sys
sys.path.insert(0, '/app/backend')

from app.database import SessionLocal
from app.models.models import Shop
import httpx

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()
print(f"Testing Content API v2 for Shop 4: {shop4.name}")

# Test with settings (cursor based) like in the example
try:
    resp = httpx.post(
        "https://content-api.wildberries.ru/content/v2/get/cards/list?locale=ru",
        headers={"Authorization": shop4.api_token, "Content-Type": "application/json"},
        json={
            "settings": {
                "sort": {"ascending": False},
                "filter": {"withPhoto": -1},
                "cursor": {"limit": 1000}
            }
        },
        timeout=30
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    cards = data.get("cards", [])
    cursor = data.get("cursor", {})
    print(f"Cards count: {len(cards)}")
    print(f"Cursor: {cursor}")
    
    if cards:
        print(f"First card: {cards[0]}")
    
    # Also try without filter settings
    resp2 = httpx.post(
        "https://content-api.wildberries.ru/content/v2/get/cards/list",
        headers={"Authorization": shop4.api_token, "Content-Type": "application/json"},
        json={"limit": 100, "offset": 0},
        timeout=30
    )
    print(f"\nSimple params - Cards: {len(resp2.json().get('cards', []))}")
    
except Exception as e:
    print(f"Error: {e}")

db.close()
