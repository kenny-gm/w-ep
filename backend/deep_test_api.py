#!/usr/bin/env python3
"""测试更多参数组合"""
from app.database import SessionLocal
from app.models.models import Shop
import httpx
import json

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token

print("=" * 70)
print("深度测试 Content API 参数")
print("=" * 70)

headers = {"Authorization": token, "Content-Type": "application/json"}
url = "https://content-api.wildberries.ru/content/v2/get/cards/list"

test_params = [
    # 基础参数
    {"limit": 1},
    {"limit": 10},
    {"limit": 50},
    {"limit": 100},
    
    # 排序参数
    {"limit": 10, "sort": {"column": "createdAt", "order": "asc"}},
    {"limit": 10, "sort": {"column": "updatedAt", "order": "desc"}},
    {"limit": 10, "sort": {"column": "nmId", "order": "asc"}},
    
    # 过滤参数
    {"limit": 10, "filter": {"withPhoto": -1}},
    {"limit": 10, "filter": {"withPhoto": 0}},
    {"limit": 10, "filter": {"withPhoto": 1}},
    {"limit": 10, "filter": {"verified": True}},
    {"limit": 10, "filter": {"archive": False}},
    {"limit": 10, "filter": {"in_trash": False}},
    {"limit": 10, "filter": {"is_discount": False}},
    
    # 组合参数
    {"limit": 50, "sort": {"column": "createdAt", "order": "desc"}, "locale": "ru"},
    {"limit": 50, "sort": {"column": "createdAt", "order": "desc"}, "locale": "en"},
    {"limit": 50, "sort": {"column": "createdAt", "order": "desc"}, "locale": "zh"},
]

with httpx.Client(timeout=15.0) as client:
    for params in test_params:
        try:
            resp = client.post(url, headers=headers, json=params)
            data = resp.json()
            cards = len(data.get("cards", []))
            cursor = data.get("cursor", {})
            
            status = "❌" if cards == 0 else "✅"
            print(f"{status} {json.dumps(params, ensure_ascii=False)[:60]}: cards={cards}")
        except Exception as e:
            print(f"❌ 错误: {str(e)[:50]}")

print("\n" + "=" * 70)
print("测试 NM ID 查询")
print("=" * 70)

# 测试通过nmID查询
nm_ids = [1, 100, 1000, 10000, 100000]
for nm_id in nm_ids:
    try:
        resp = client.post(url, headers=headers, json={"nmId": nm_id})
        data = resp.json()
        cards = data.get("cards", [])
        if cards:
            print(f"✅ nmID={nm_id}: 找到产品 - {cards[0].get('vendorCode', 'N/A')}")
        else:
            print(f"❌ nmID={nm_id}: 未找到")
    except Exception as e:
        print(f"❌ nmID={nm_id}: 错误")

db.close()
