import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 4).first()
client = WBAPIClient(shop.api_token)

# Get one product to show all fields
products = client.get_products(limit=1, offset=0, locale="ru")
if products:
    import json
    print(json.dumps(products[0], indent=2, ensure_ascii=False))

db.close()
