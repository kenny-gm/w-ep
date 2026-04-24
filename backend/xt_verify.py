import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop4 = db.query(Shop).filter(Shop.id == 4).first()
client = WBAPIClient(shop4.api_token)

products = client.get_products_from_statistics()
print(f"Products from API: {len(products)}")

for p in products:
    nm_id = str(p.get("nmID", p.get("nmId", "")))
    print(f"  Extracted nm_id: '{nm_id}' from keys {list(p.keys())}")

db.close()
