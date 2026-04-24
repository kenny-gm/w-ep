import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()
client = WBAPIClient(shop4.api_token)

# Get raw response from stocks API
print("=== Raw Stocks API Response ===")
try:
    resp = client._request("GET", "statistics", "/api/v1/supplier/stocks", params={"dateFrom": "2020-01-01"})
    print(f"Type: {type(resp)}")
    print(f"Length: {len(resp) if isinstance(resp, list) else 'N/A'}")
    print(f"Full response (first 2000 chars):\n{str(resp)[:2000]}")
except Exception as e:
    print(f"Error: {e}")

# Try the orders statistics endpoint
print("\n=== Raw Orders Stats Response ===")
try:
    resp = client._request("POST", "orders", "/v2/supplier/orders/statistics", json_data={"limit": 1000})
    print(f"Response: {str(resp)[:1000]}")
except Exception as e:
    print(f"Error: {e}")

db.close()
