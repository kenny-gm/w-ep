#!/usr/bin/env python3
"""测试更多normquery参数"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop
from datetime import datetime, timedelta

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

headers = {"Authorization": shop.api_token, "Content-Type": "application/json"}
client = httpx.Client(timeout=30)

date_to = datetime.now().strftime("%Y-%m-%d")
date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

# 尝试不同的API
apis = [
    ("POST", "https://advert-api.wildberries.ru/adv/v1/normquery/stats", {"from": date_from, "to": date_to}),
    ("POST", "https://advert-api.wildberries.ru/adv/v1/normquery/stats", {"dateFrom": date_from, "dateTo": date_to}),
]

for method, url, params in apis:
    resp = client.post(url, headers=headers, json=params)
    print(f"\n{method} {url.split('ru/')[1]}")
    print(f"参数: {params}")
    print(f"状态: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"响应: {str(data)[:200]}")
    else:
        print(f"错误: {resp.text[:100]}")

db.close()
