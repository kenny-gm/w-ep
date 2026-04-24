#!/usr/bin/env python3
"""测试广告API"""
from app.database import SessionLocal
from app.models.models import Shop
from app.services.wb_api import WBAPIClient
import httpx
from datetime import datetime, timedelta

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

print("=" * 70)
print("测试广告API")
print("=" * 70)
print(f"店铺: {shop.name}")

# 直接用httpx测试
headers = {"Authorization": shop.api_token, "Content-Type": "application/json"}
client = httpx.Client(timeout=15)

# 1. 测试广告列表
print("\n【1】GET /api/advert/v2/adverts")
resp = client.get("https://advert-api.wildberries.ru/api/advert/v2/adverts", headers=headers)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"数据类型: {type(data)}")
    if isinstance(data, list):
        print(f"广告数量: {len(data)}")
        if data:
            print(f"第一条: {data[0]}")
    else:
        print(f"响应: {str(data)[:200]}")
else:
    print(f"错误: {resp.text[:200]}")

# 2. 测试广告统计
print("\n【2】GET /api/advert/v1/reports")
date_to = datetime.now().strftime("%Y-%m-%d")
date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
params = {"dateFrom": date_from, "dateTo": date_to, "ids": ""}

resp = client.get("https://advert-api.wildberries.ru/api/advert/v1/reports", 
                  headers=headers, params=params)
print(f"状态码: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"响应类型: {type(data)}")
    print(f"响应: {str(data)[:200]}")
else:
    print(f"错误: {resp.text[:200]}")

client.close()
db.close()
