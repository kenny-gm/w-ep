import sys
sys.path.insert(0, '/app/backend')

from app.services.platform_client import get_platform_client, PLATFORM_CLIENTS
from app.database import SessionLocal
from app.models.models import Shop

print("Registered platforms:", list(PLATFORM_CLIENTS.keys()))

db = SessionLocal()
for shop in db.query(Shop).all():
    print(f"\nShop {shop.id}: {shop.name} ({shop.platform})")
    try:
        client = get_platform_client(shop.platform, shop.api_token)
        print(f"  Client: {client.__class__.__name__}")
        print(f"  Connection test: {client.test_connection()}")
    except Exception as e:
        print(f"  Error: {e}")

db.close()
