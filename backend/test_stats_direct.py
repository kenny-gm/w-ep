#!/usr/bin/env python3
"""直接测试Statistics API"""
from app.database import SessionLocal
from app.models.models import Shop
import httpx

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token
db.close()

headers = {"Authorization": token, "Content-Type": "application/json"}
client = httpx.Client(timeout=30)

print("测试Statistics订单API:")
resp = client.get(
    "https://statistics-api.wildberries.ru/api/v1/supplier/orders",
    headers=headers,
    params={"dateFrom": "2026-01-01"}
)
print(f"状态: {resp.status_code}")
if resp.status_code == 200:
    orders = resp.json()
    print(f"订单数量: {len(orders)}")
    if orders:
        print(f"第一条: {str(orders[0])[:100]}")
else:
    print(f"错误: {resp.text[:100]}")

print("\n测试Statistics产品API:")
resp = client.get(
    "https://statistics-api.wildberries.ru/api/v1/supplier/stocks",
    headers=headers,
    params={"dateFrom": "2020-01-01"}
)
print(f"状态: {resp.status_code}")
if resp.status_code == 200:
    stocks = resp.json()
    print(f"库存: {len(stocks)}")
    unique = {}
    for s in stocks:
        nm_id = s.get("nmId")
        if nm_id and nm_id not in unique:
            unique[nm_id] = s
    print(f"唯一商品: {len(unique)}")

client.close()
