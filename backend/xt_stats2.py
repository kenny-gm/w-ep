import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop
import httpx

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()

# Direct API calls
print("=== Testing different WB API endpoints ===")

headers = {"Authorization": shop4.api_token}

# Try orders API
print("\n--- Orders API ---")
try:
    resp = httpx.post("https://market-api.wildberries.ru/api/v2/orders", 
                     headers=headers, json={"limit": 100}, timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:300]}")
except Exception as e:
    print(f"Error: {e}")

# Try sales API
print("\n--- Sales API ---")
try:
    resp = httpx.post("https://market-api.wildberries.ru/api/v1/supplier/sales",
                     headers=headers, json={"limit": 100, "dateFrom": "2026-01-01"}, timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

db.close()
