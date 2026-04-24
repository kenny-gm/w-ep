import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()
client = WBAPIClient(shop4.api_token)

# Get all products from Statistics API
print("=== Statistics API (Stocks) ===")
try:
    response = client._request("GET", "statistics", "/api/v1/supplier/stocks", params={"dateFrom": "2020-01-01"})
    print(f"Type: {type(response)}")
    if isinstance(response, list):
        print(f"Total items: {len(response)}")
        for item in response[:20]:
            print(f"  nmId={item.get('nmId')}, article={item.get('supplierArticle')}, qty={item.get('quantityFull')}")
except Exception as e:
    print(f"Error: {e}")

# Also try the cards API
print("\n=== Content API (Cards) ===")
cards = client.get_products(limit=100, offset=0, locale="ru")
print(f"Total cards: {len(cards)}")
for c in cards[:5]:
    print(f"  {c}")

db.close()
