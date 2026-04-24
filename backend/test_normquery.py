#!/usr/bin/env python3
"""测试normquery/stats API"""
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

print("=== 测试 normquery/stats API ===")
url = "https://advert-api.wildberries.ru/adv/v1/normquery/stats"
print(f"请求: POST {url}")

# 尝试不同的参数格式
params_list = [
    {"beginDate": date_from, "endDate": date_to, "limit": 10},
    {"dateFrom": date_from, "dateTo": date_to, "limit": 10},
    {"from": date_from, "to": date_to},
]

for params in params_list:
    resp = client.post(url, headers=headers, json=params)
    print(f"\n参数: {params}")
    print(f"状态: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"响应: {str(data)[:300]}")
        break
    else:
        print(f"错误: {resp.text[:100]}")

db.close()
