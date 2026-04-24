import sys
sys.path.insert(0, '/app/backend')

from app.services.wb_api import WBAPIClient
from app.database import SessionLocal
from app.models.models import Shop
import requests

db = SessionLocal()

shop4 = db.query(Shop).filter(Shop.id == 4).first()
client = WBAPIClient(shop4.api_token)

# Try different Statistics API endpoints
endpoints = [
    ("GET", "statistics", "/api/v1/supplier/stocks", {"dateFrom": "2020-01-01"}),
    ("POST", "content", "/v1/cards/list", {}),
    ("GET", "statistics", "/api/v1/supplier/products", {}),
]

for method, api, path, params in endpoints:
    print(f"\n=== {method} {path} ===")
    try:
        if method == "GET":
            resp = requests.get(f"https://statistics-api.wildberries.ru{path}", 
                              headers=client.headers, params=params, timeout=30)
        else:
            resp = requests.post(f"https://market-api.wildberries.ru{path}",
                               headers=client.headers, json=params, timeout=30)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        if isinstance(data, list):
            print(f"Items: {len(data)}")
            for item in data[:3]:
                print(f"  {item}")
        elif isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
            if "data" in data:
                print(f"Data items: {len(data.get('data', []))}")
    except Exception as e:
        print(f"Error: {e}")

db.close()
