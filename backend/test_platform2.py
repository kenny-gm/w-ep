import sys
sys.path.insert(0, '/app/backend')

# 必须先导入 wb_api 以触发注册
from app.services import wb_api
from app.services import yandex_client
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
    except Exception as e:
        print(f"  Error: {e}")

db.close()
