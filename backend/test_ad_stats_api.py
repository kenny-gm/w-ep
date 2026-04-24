#!/usr/bin/env python3
"""测试广告统计API"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop
from datetime import datetime, timedelta

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

headers = {"Authorization": shop.api_token}
client = httpx.Client(timeout=30)

date_to = datetime.now().strftime("%Y-%m-%d")
date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

print("测试广告统计API端点:")

endpoints = [
    ("GET", "https://advert-api.wildberries.ru/api/advert/v1/report"),
    ("GET", "https://advert-api.wildberries.ru/api/advert/v1/reports"),
    ("GET", "https://advert-api.wildberries.ru/api/advert/v1/history"),
]

for method, url in endpoints:
    try:
        if method == "GET":
            resp = client.get(url, headers=headers, params={"dateFrom": date_from, "dateTo": date_to})
        print(f"{method} {url.split('ru/')[-1]}: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"  响应keys: {list(data.keys())[:5]}")
    except Exception as e:
        print(f"{method} {url.split('ru/')[-1]}: 错误 - {str(e)[:30]}")

db.close()
