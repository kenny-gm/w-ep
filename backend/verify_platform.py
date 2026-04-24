import sys
sys.path.insert(0, '/app/backend')

from app.services.platform_client import get_platform_client, PLATFORM_CLIENTS
from app.database import SessionLocal
from app.models.models import Shop

print("Registered platforms:", list(PLATFORM_CLIENTS.keys()))

db = SessionLocal()
for shop in db.query(Shop).all():
    print(f"Shop {shop.id}: {shop.name} ({shop.platform}) -> {get_platform_client(shop.platform, shop.api_token).__class__.__name__}")

db.close()
print("\n多平台架构已就绪！")
