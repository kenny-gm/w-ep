#!/usr/bin/env python3
"""按照排查建议测试"""
import httpx
import json
from app.database import SessionLocal
from app.models.models import Shop

# 获取Token
db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token
db.close()

print("=" * 70)
print("按照排查建议测试")
print("=" * 70)

headers = {"Authorization": token, "Content-Type": "application/json"}
client = httpx.Client(timeout=15)

# 1. 最简请求
print("\n【测试1】最简请求: limit=10")
resp = client.post(
    "https://content-api.wildberries.ru/content/v2/get/cards/list",
    headers=headers,
    json={"limit": 10}
)
data = resp.json()
print(f"状态: {resp.status_code}")
print(f"响应: {json.dumps(data)}")

# 2. 空请求
print("\n【测试2】空请求: {}")
resp = client.post(
    "https://content-api.wildberries.ru/content/v2/get/cards/list",
    headers=headers,
    json={}
)
data = resp.json()
print(f"状态: {resp.status_code}")
print(f"响应: {json.dumps(data)}")

# 3. locale=ru
print("\n【测试3】locale=ru")
resp = client.post(
    "https://content-api.wildberries.ru/content/v2/get/cards/list",
    headers=headers,
    json={"limit": 10, "locale": "ru"}
)
data = resp.json()
print(f"状态: {resp.status_code}")
print(f"响应: {json.dumps(data)}")

# 4. 完整响应结构
print("\n【测试4】响应结构检查")
resp = client.post(
    "https://content-api.wildberries.ru/content/v2/get/cards/list",
    headers=headers,
    json={"limit": 10}
)
data = resp.json()
print("响应keys:", list(data.keys()))

# 5. 测试/v1端点
print("\n【测试5】v1端点")
resp = client.post(
    "https://content-api.wildberries.ru/content/v1/cards",
    headers=headers,
    json={}
)
print(f"  /content/v1/cards: {resp.status_code}")

# 6. 订单API
print("\n【测试6】订单API")
resp = client.get(
    "https://marketplace-api.wildberries.ru/api/v3/orders/new",
    headers=headers
)
print(f"  /api/v3/orders/new: {resp.status_code}")
print(f"    {resp.text[:150]}")

client.close()
