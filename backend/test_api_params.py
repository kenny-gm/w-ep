#!/usr/bin/env python3
"""测试不同的API参数组合"""
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

url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
headers = {"Authorization": token, "Content-Type": "application/json"}

print("="*60)
print("测试不同的请求参数组合")
print("="*60)

# 测试不同的参数组合
test_cases = [
    {"name": "测试1: 空参数", "body": {}},
    {"name": "测试2: 只有limit", "body": {"limit": 100}},
    {"name": "测试3: limit+offset", "body": {"limit": 100, "offset": 0}},
    {"name": "测试4: limit+offset+locale", "body": {"limit": 100, "offset": 0, "locale": "ru"}},
    {"name": "测试5: limit+locale", "body": {"limit": 100, "locale": "ru"}},
    {"name": "测试6: 带withPhoto", "body": {"limit": 100, "withPhoto": True}},
    {"name": "测试7: 带sort", "body": {"limit": 100, "sort": {"column": "createdAt", "order": "desc"}}},
]

for test in test_cases:
    print(f"\n{test['name']}")
    print(f"请求体: {json.dumps(test['body'], ensure_ascii=False)}")
    
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, headers=headers, json=test['body'])
            print(f"状态码: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                cards = data.get('cards', [])
                total = data.get('cursor', {}).get('total', 0)
                print(f"✅ cards数量: {len(cards)}, total: {total}")
                
                if cards:
                    print(f"第一个产品: nmID={cards[0].get('nmID')}, name={cards[0].get('name')}")
                    print(f"完整数据: {json.dumps(cards[0], ensure_ascii=False, indent=2)[:500]}")
            else:
                print(f"响应: {resp.text[:300]}")
    except Exception as e:
        print(f"错误: {e}")

# 测试其他产品API
print("\n" + "="*60)
print("测试其他产品API端点")
print("="*60)

other_endpoints = [
    {
        "name": "Marketplace items",
        "url": "https://marketplace-api.wildberries.ru/api/v3/items",
        "method": "GET"
    },
    {
        "name": "Content cards cursor list",
        "url": "https://content-api.wildberries.ru/content/v2/get/cards/cursor/list",
        "method": "POST",
        "body": {"limit": 100}
    },
]

for ep in other_endpoints:
    print(f"\n{ep['name']}")
    print(f"URL: {ep['url']}")
    
    try:
        with httpx.Client(timeout=15.0) as client:
            if ep['method'] == "GET":
                resp = client.get(ep['url'], headers=headers)
            else:
                resp = client.post(ep['url'], headers=headers, json=ep.get('body', {}))
            
            print(f"状态码: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"响应: {json.dumps(data, ensure_ascii=False)[:300]}")
            else:
                print(f"响应: {resp.text[:200]}")
    except Exception as e:
        print(f"错误: {e}")
