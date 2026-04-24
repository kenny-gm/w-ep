import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()
client = WBAPIClient(shop4.api_token)

print("=== get_products_from_statistics() ===")
products = client.get_products_from_statistics()
print(f"Total: {len(products)}")
for p in products:
    print(f"  nmId={p.get('nmId')}, article={p.get('supplierArticle')}")

print("\n=== get_products() ===")
cards = client.get_products(limit=100, offset=0, locale="ru")
print(f"Total: {len(cards)}")

print("\n=== get_products_all() ===")
all_prods = client.get_products_all(locale="ru")
print(f"Total: {len(all_prods)}")

db.close()
