#!/usr/bin/env python3
"""详细检查Token和API"""
import httpx
import json
import base64
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token

# 解析Token
parts = token.split(".")
payload = json.loads(base64.b64decode(parts[1] + "=" * (4 - len(parts[1]) % 4)))

print("=" * 70)
print("Token Payload 完整信息:")
print("=" * 70)
for k, v in payload.items():
    print(f"  {k}: {v}")

db.close()

headers = {"Authorization": token, "Content-Type": "application/json"}
client = httpx.Client(timeout=15)

print("\n" + "=" * 70)
print("测试不同API:")
print("=" * 70)

# 1. 卖家信息
print("\n【卖家信息API】")
apis = [
    "https://supplier-api.wildberries.ru/api/v1/supplier/info",
    "https://marketplace-api.wildberries.ru/api/v3/seller-info",
]
for api in apis:
    resp = client.get(api, headers=headers)
    print(f"  {api.split('ru/')[-1]}: {resp.status_code}")
    if resp.status_code == 200:
        print(f"    {resp.text[:200]}")

# 2. 商品数量
print("\n【商品数量】")
resp = client.get("https://content-api.wildberries.ru/content/v1/nmcard/count", headers=headers)
print(f"  /content/v1/nmcard/count: {resp.status_code}")
print(f"    {resp.text[:100]}")

# 3. 用不同方式查询
print("\n【不同查询方式】")
# 方式1: GET with params
resp = client.get(
    "https://content-api.wildberries.ru/content/v2/get/cards/list",
    headers=headers,
    params={"limit": 10}
)
print(f"  GET with params: {resp.status_code}, {resp.text[:100]}")

client.close()
