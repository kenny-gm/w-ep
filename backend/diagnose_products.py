#!/usr/bin/env python3
"""诊断产品同步问题"""
from app.database import SessionLocal
from app.models.models import Product, Shop
import json
import base64
import httpx

db = SessionLocal()

print("=" * 70)
print("产品同步诊断")
print("=" * 70)

# 1. 检查数据库产品数量
product_count = db.query(Product).count()
print(f"\n【1】数据库产品数量: {product_count}")

# 2. 检查店铺Token
print("\n【2】店铺Token信息:")
shops = db.query(Shop).all()
for shop in shops:
    token = shop.api_token
    print(f"\n  店铺: {shop.name}")
    print(f"  Token长度: {len(token) if token else 0}")

    if token and len(token) > 100:
        parts = token.split('.')
        if len(parts) >= 2:
            try:
                payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
                decoded = json.loads(base64.b64decode(payload))
                print(f"  UID (用户ID): {decoded.get('uid')}")
                print(f"  OID (组织ID): {decoded.get('oid')}")
                print(f"  过期时间: {decoded.get('exp')}")
            except Exception as e:
                print(f"  JWT解码错误: {e}")

# 3. 直接测试WB API
print("\n【3】直接测试WB API:")
for shop in shops:
    if not shop.api_token:
        continue

    print(f"\n  测试店铺: {shop.name}")
    url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
    headers = {
        "Authorization": shop.api_token,
        "Content-Type": "application/json"
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, headers=headers, json={"limit": 100})
            print(f"  状态码: {resp.status_code}")

            if resp.status_code == 200:
                data = resp.json()
                cards = data.get('cards', [])
                cursor = data.get('cursor', {})
                print(f"  cards数量: {len(cards)}")
                print(f"  cursor: {cursor}")

                if cards:
                    print(f"  第一个产品:")
                    first = cards[0]
                    print(f"    nmID: {first.get('nmID')}")
                    print(f"    vendorCode: {first.get('vendorCode')}")
            else:
                print(f"  错误: {resp.text[:200]}")
    except Exception as e:
        print(f"  请求失败: {e}")

# 4. 测试其他WB API端点
print("\n【4】测试其他API端点:")
shop = db.query(Shop).filter(Shop.id == 2).first()
if shop and shop.api_token:
    headers = {
        "Authorization": shop.api_token,
        "Content-Type": "application/json"
    }

    # 测试卖家信息
    print("\n  卖家信息:")
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                "https://marketplace-api.wildberries.ru/api/v3/seller/info",
                headers=headers
            )
            print(f"  状态码: {resp.status_code}")
            if resp.status_code == 200:
                print(f"  响应: {resp.text[:200]}")
            else:
                print(f"  错误: {resp.text[:150]}")
    except Exception as e:
        print(f"  失败: {e}")

db.close()
