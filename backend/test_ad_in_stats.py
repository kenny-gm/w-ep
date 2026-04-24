#!/usr/bin/env python3
"""检查Statistics API中的广告数据"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop
from datetime import datetime, timedelta

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

headers = {"Authorization": shop.api_token}
client = httpx.Client(timeout=30)

date_to = datetime.now().strftime("%Y-%m-%d")
date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

print("=== Statistics API 销售数据 ===")
resp = client.get(
    "https://statistics-api.wildberries.ru/api/v1/supplier/sales",
    headers=headers,
    params={"dateFrom": date_from, "dateTo": date_to}
)
print(f"状态: {resp.status_code}")
if resp.status_code == 200:
    sales = resp.json()
    print(f"销售记录数: {len(sales)}")
    if sales:
        print(f"第一条: {sales[0]}")
        # 查找广告相关字段
        ad_keys = [k for k in sales[0].keys() if 'ad' in k.lower() or 'spent' in k.lower()]
        print(f"广告相关字段: {ad_keys}")

db.close()
