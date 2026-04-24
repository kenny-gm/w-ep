#!/usr/bin/env python3
"""测试所有可能的产品API"""
import httpx
import json
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token if shop else None
db.close()

if not token:
    print("没有Token")
    exit()

headers = {"Authorization": token, "Content-Type": "application/json"}

# 测试所有可能的产品相关API
apis = [
    # Content API
    ("GET", "https://content-api.wildberries.ru/content/v1/cards/list", {}),
    ("POST", "https://content-api.wildberries.ru/content/v1/cards/list", {"limit": 100}),
    ("GET", "https://content-api.wildberries.ru/content/v2/cards/list", {}),
    ("POST", "https://content-api.wildberries.ru/content/v2/cards/list", {"limit": 100}),
    ("GET", "https://content-api.wildberries.ru/content/v2/get/cards/list", {}),
    ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {"limit": 10}),
    ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {}),
    
    # 不同的店铺参数
    ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {"limit": 10, "shopId": 250042561}),
    ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {"limit": 10, "supplierId": 302238568}),
    ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {"limit": 10, "userId": 302238568}),
    
    # 使用过滤
    ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/filter", {"limit": 10}),
]

print("测试所有Content API端点")
print("="*70)

for method, url, body in apis:
    print(f"\n{method} {url}")
    print(f"Body: {json.dumps(body)}")
    
    try:
        with httpx.Client(timeout=15.0) as client:
            if method == "GET":
                resp = client.get(url, headers=headers)
            else:
                resp = client.post(url, headers=headers, json=body if body else None)
            
            print(f"状态码: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict):
                    cards = data.get('cards', [])
                    total = data.get('cursor', {}).get('total', 0)
                    print(f"✅ cards: {len(cards)}, total: {total}")
                    if cards:
                        print(f"第一个: {cards[0]}")
                else:
                    print(f"响应类型: {type(data)}, 长度: {len(data) if isinstance(data, list) else 'N/A'}")
            else:
                print(f"响应: {resp.text[:150]}")
    except Exception as e:
        print(f"错误: {e}")
