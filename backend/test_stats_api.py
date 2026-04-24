#!/usr/bin/env python3
"""测试Statistics API获取商品"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop
from datetime import datetime, timedelta

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token
db.close()

headers = {"Authorization": token, "Content-Type": "application/json"}
client = httpx.Client(timeout=30)

print("=" * 70)
print("测试Statistics API获取商品数据")
print("=" * 70)

# 1. 库存报表
print("\n【1】库存报表 /api/v1/supplier/stocks")
resp = client.get("https://statistics-api.wildberries.ru/api/v1/supplier/stocks",
                  headers=headers,
                  params={"dateFrom": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")})
print(f"状态: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✅ 成功! 数据类型: {type(data)}")
    if isinstance(data, list):
        print(f"   数量: {len(data)}")
        if data:
            print(f"   第一条: {str(data[0])[:150]}")
else:
    print(f"错误: {resp.text[:100]}")

# 2. 订单报表
print("\n【2】订单报表 /api/v1/supplier/orders")
resp = client.get("https://statistics-api.wildberries.ru/api/v1/supplier/orders",
                  headers=headers,
                  params={"dateFrom": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")})
print(f"状态: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✅ 成功! 数据类型: {type(data)}")
    if isinstance(data, list):
        print(f"   数量: {len(data)}")
        if data:
            print(f"   第一条: {str(data[0])[:150]}")
else:
    print(f"错误: {resp.text[:100]}")

# 3. 销售报表
print("\n【3】销售报表 /api/v1/supplier/sales")
resp = client.get("https://statistics-api.wildberries.ru/api/v1/supplier/sales",
                  headers=headers,
                  params={"dateFrom": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")})
print(f"状态: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(f"✅ 成功! 数据类型: {type(data)}")
    if isinstance(data, list):
        print(f"   数量: {len(data)}")
        if data:
            print(f"   第一条: {str(data[0])[:150]}")
else:
    print(f"错误: {resp.text[:100]}")

client.close()
