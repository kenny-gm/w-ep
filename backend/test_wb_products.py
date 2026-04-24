import sys
sys.path.insert(0, '/app/backend')

from app.database import SessionLocal
from app.models.models import Shop
import httpx

db = SessionLocal()

# Test all shops with content API
for shop_id in [1, 4]:
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    print(f"\n=== Shop {shop_id}: {shop.name} ===")
    
    # Try the v2 content API with recursive/cursor
    try:
        resp = httpx.post(
            "https://content-api.wildberries.ru/content/v2/get/cards/list",
            headers={"Authorization": shop.api_token, "Content-Type": "application/json"},
            json={"limit": 1000, "offset": 0},
            timeout=30
        )
        data = resp.json()
        cards = data.get("cards", [])
        cursor = data.get("cursor", {})
        print(f"Cards: {len(cards)}, Cursor: {cursor}")
        
        # Try with different settings
        resp2 = httpx.post(
            "https://content-api.wildberries.ru/content/v2/get/cards/list",
            headers={"Authorization": shop.api_token, "Content-Type": "application/json"},
            json={"settings": {"with_hibernate": "true", "limit": 1000}},
            timeout=30
        )
        data2 = resp2.json()
        cards2 = data2.get("cards", [])
        print(f" With settings: {len(cards2)} cards")
        
    except Exception as e:
        print(f"Error: {e}")

db.close()
