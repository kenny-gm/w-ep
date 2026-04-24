import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop, Product
import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("sync")

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()
print(f"Shop 4: {shop4.name}")
print(f"  API Token: {shop4.api_token[:30]}...")

client = WBAPIClient(shop4.api_token)

# Step 1: Get products from Content API
cards = client.get_products(limit=10, offset=0, locale="ru")
print(f"\nContent API returned: {len(cards)} products")

# Step 2: If empty, try Statistics API
if not cards:
    cards = client.get_products_from_statistics()
    print(f"Statistics API returned: {len(cards)} products")
    
    if cards:
        print(f"First card keys: {cards[0].keys()}")
        print(f"First card: {cards[0]}")
        
        # Try to extract nm_id
        nm_id = str(cards[0].get("nmID", cards[0].get("nmId", "")))
        print(f"Extracted nm_id: '{nm_id}'")
        
        # Try to save
        if nm_id:
            existing = db.query(Product).filter(
                Product.nm_id == nm_id,
                Product.shop_id == 4
            ).first()
            print(f"Existing product with this nm_id: {existing}")

db.close()
