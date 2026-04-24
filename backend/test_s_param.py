#!/usr/bin/env python3
"""测试s参数"""
import httpx
import json
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token
db.close()

headers = {"Authorization": token, "Content-Type": "application/json"}
client = httpx.Client(timeout=15)

print("测试不同参数组合:")

# 1. 基础
resp = client.post(
    "https://content-api.wildberries.ru/content/v2/get/cards/list",
    headers=headers,
    json={"limit": 10}
)
data = resp.json()
print(f"1. limit=10: cards={len(data.get('cards', []))}, total={data.get('cursor',{}).get('total',0)}")

# 2. 带s参数
resp = client.post(
    "https://content-api.wildberries.ru/content/v2/get/cards/list",
    headers=headers,
    json={"limit": 10, "s": "1073756902"}
)
data = resp.json()
print(f"2. limit=10, s='1073756902': cards={len(data.get('cards', []))}, total={data.get('cursor',{}).get('total',0)}")

# 3. supplierId
resp = client.post(
    "https://content-api.wildberries.ru/content/v2/get/cards/list",
    headers=headers,
    json={"limit": 10, "supplierId": 1073756902}
)
data = resp.json()
print(f"3. limit=10, supplierId=1073756902: cards={len(data.get('cards', []))}, total={data.get('cursor',{}).get('total',0)}")

# 4. 用nm查询
resp = client.post(
    "https://content-api.wildberries.ru/content/v2/get/cards/list",
    headers=headers,
    json={"nmId": 1}
)
data = resp.json()
print(f"4. nmId=1: cards={len(data.get('cards', []))}")

client.close()
print("\n测试完成")
