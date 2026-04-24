#!/usr/bin/env python3
"""全面测试WB API"""
from app.database import SessionLocal
from app.models.models import Shop
import httpx
import json

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token

print("=" * 70)
print("WB API 全面测试")
print("=" * 70)
print(f"\n店铺: {shop.name}")
print(f"Token长度: {len(token)}")

headers = {"Authorization": token, "Content-Type": "application/json"}

with httpx.Client(timeout=30.0) as client:
    # 1. 测试不同的Content API端点
    print("\n【1】Content API - 商品列表")
    endpoints = [
        ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {}),
        ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {"limit": 100}),
        ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {"limit": 100, "offset": 0}),
        ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {"limit": 100, "locale": "ru"}),
        ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {"limit": 100, "filter": {}}),
        ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {"limit": 100, "filter": {"withPhoto": -1}}),
        ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {"limit": 100, "filter": {"allowedCategoriesOnly": False}}),
    ]

    for method, url, body in endpoints:
        try:
            resp = client.post(url, headers=headers, json=body)
            data = resp.json()
            cards = len(data.get("cards", []))
            total = data.get("cursor", {}).get("total", 0)
            print(f"  {url.split('/')[-1]}: 状态={resp.status_code}, cards={cards}, total={total}")
        except Exception as e:
            print(f"  {url.split('/')[-1]}: 错误={str(e)[:50]}")

    # 2. 测试其他Content端点
    print("\n【2】其他Content端点")
    other_endpoints = [
        ("GET", "https://content-api.wildberries.ru/content/v2/object/parent/all"),
        ("GET", "https://content-api.wildberries.ru/content/v2/cards/list"),
        ("POST", "https://content-api.wildberries.ru/content/v2/cards/list", {}),
    ]

    for method, url, *body in other_endpoints:
        try:
            if method == "GET":
                resp = client.get(url, headers=headers)
            else:
                resp = client.post(url, headers=headers, json=body[0] if body else {})
            print(f"  {url.split('ru/')[-1]}: 状态={resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict):
                    print(f"    keys: {list(data.keys())[:5]}")
                elif isinstance(data, list):
                    print(f"    数量: {len(data)}")
        except Exception as e:
            print(f"  {url.split('ru/')[-1]}: 错误={str(e)[:50]}")

    # 3. 测试Marketplace API
    print("\n【3】Marketplace API")
    mp_endpoints = [
        ("GET", "https://marketplace-api.wildberries.ru/api/v3/warehouses"),
        ("GET", "https://marketplace-api.wildberries.ru/api/v3/orders/new"),
        ("GET", "https://marketplace-api.wildberries.ru/api/v3/orders", {"date_start": "2026-01-01", "date_end": "2026-03-21"}),
    ]

    for method, url, *params in mp_endpoints:
        try:
            if method == "GET":
                resp = client.get(url, headers=headers, params=params[0] if params else None)
            print(f"  {url.split('ru/')[-1]}: 状态={resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"    数据: {json.dumps(data, ensure_ascii=False)[:100]}")
            else:
                print(f"    错误: {resp.text[:100]}")
        except Exception as e:
            print(f"  错误: {str(e)[:50]}")

    # 4. 测试统计API
    print("\n【4】统计API")
    stats_endpoints = [
        ("GET", "https://statistics-api.wildberries.ru/api/v1/supplier/incomes"),
        ("GET", "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"),
    ]

    for method, url in stats_endpoints:
        try:
            resp = client.get(url, headers=headers)
            print(f"  {url.split('ru/')[-1]}: 状态={resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"    数据类型: {type(data)}")
            else:
                print(f"    错误: {resp.text[:100]}")
        except Exception as e:
            print(f"  错误: {str(e)[:50]}")

db.close()
