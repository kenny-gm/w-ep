#!/usr/bin/env python3
"""深度测试Content API"""
import httpx
import json
import base64
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token
db.close()

# 解析Token权限
parts = token.split(".")
payload = json.loads(base64.b64decode(parts[1] + "=" * (4 - len(parts[1]) % 4)))
s_value = payload.get("s", 0)

print("Token s字段:", s_value)
print("二进制:", bin(s_value))
print("权限:", "Content" if s_value & 1 else "无Content")

headers = {"Authorization": token, "Content-Type": "application/json"}
client = httpx.Client(timeout=10)

# 测试Content API
print("\n测试Content API:")
resp = client.post(
    "https://content-api.wildberries.ru/content/v2/get/cards/list",
    headers=headers,
    json={"limit": 10}
)
print(f"状态: {resp.status_code}")
data = resp.json()
print(f"cards: {len(data.get('cards', []))}")
print(f"cursor: {data.get('cursor')}")

client.close()
