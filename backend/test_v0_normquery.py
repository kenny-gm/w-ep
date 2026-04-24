#!/usr/bin/env python3
"""测试 v0/normquery/stats API"""
import httpx
import json
from app.database import SessionLocal
from app.models.models import Shop
from datetime import datetime, timedelta

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

headers = {"Authorization": shop.api_token, "Content-Type": "application/json"}
client = httpx.Client(timeout=30)

date_to = datetime.now().strftime("%Y-%m-%d")
date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

print("=== 测试 v0/normquery/stats API ===")
url = "https://advert-api.wildberries.ru/adv/v0/normquery/stats"

params = {"from": date_from, "to": date_to}
resp = client.post(url, headers=headers, json=params)
print(f"参数: {params}")
print(f"状态: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")

db.close()
