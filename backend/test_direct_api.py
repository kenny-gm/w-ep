#!/usr/bin/env python3
"""直接测试WB API并打印完整响应"""
import httpx
import json
from app.database import SessionLocal
from app.models.models import Shop

# 获取Token
db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 1).first()
if not shop:
    print("店铺不存在")
    exit()

token = shop.api_token
print(f"店铺: {shop.name}")
print(f"Token长度: {len(token) if token else 0}")

if not token:
    print("没有Token")
    exit()

# 测试API
url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
headers = {"Authorization": token, "Content-Type": "application/json"}

print(f"\n请求URL: {url}")
print(f"请求方法: POST")

with httpx.Client(timeout=30.0) as client:
    # 测试1: 带limit
    print("\n=== 测试1: limit=100 ===")
    resp = client.post(url, headers=headers, json={"limit": 100})
    print(f"状态码: {resp.status_code}")
    print(f"完整响应:")
    data = resp.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    # 测试2: 带更多参数
    print("\n=== 测试2: limit=100, offset=0, locale=ru ===")
    resp = client.post(url, headers=headers, json={"limit": 100, "offset": 0, "locale": "ru"})
    print(f"状态码: {resp.status_code}")
    data = resp.json()
    print(f"cards数量: {len(data.get('cards', []))}")
    print(f"cursor: {data.get('cursor')}")
    
    # 如果有cards，打印第一个
    if data.get('cards'):
        print(f"\n第一个产品:")
        print(json.dumps(data['cards'][0], indent=2, ensure_ascii=False))

db.close()
