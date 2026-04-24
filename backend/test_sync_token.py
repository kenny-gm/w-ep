#!/usr/bin/env python3
"""测试同步服务Token获取"""
from app.database import SessionLocal
from app.models.models import Shop
from app.services.wb_api import WBAPIClient
import httpx

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

print(f"店铺: {shop.name}")
token = shop.api_token
print(f"数据库Token长度: {len(token) if token else 0}")
print(f"Token前50字符: {token[:50] if token else 'None'}")
print(f"Token后50字符: {token[-50:] if token and len(token) > 50 else token}")

# 创建API客户端
client = WBAPIClient(token)
print(f"\n客户端Token长度: {len(client.api_token)}")

# 直接测试API
url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
headers = {"Authorization": token, "Content-Type": "application/json"}

with httpx.Client(timeout=15.0) as http:
    print(f"\n请求URL: {url}")
    resp = http.post(url, headers=headers, json={"limit": 10})
    print(f"状态码: {resp.status_code}")
    data = resp.json()
    print(f"cards数量: {len(data.get('cards', []))}")
    print(f"cursor: {data.get('cursor')}")

    # 如果有产品，打印第一个
    if data.get('cards'):
        print(f"\n第一个产品:")
        import json
        print(json.dumps(data['cards'][0], indent=2, ensure_ascii=False)[:500])

db.close()
