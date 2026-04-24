#!/usr/bin/env python3
"""从Statistics API获取商品列表"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token
db.close()

headers = {"Authorization": token, "Content-Type": "application/json"}
client = httpx.Client(timeout=30)

# 获取库存数据
resp = client.get(
    "https://statistics-api.wildberries.ru/api/v1/supplier/stocks",
    headers=headers,
    params={"dateFrom": "2025-01-01"}
)

if resp.status_code == 200:
    stocks = resp.json()
    print(f"库存记录数: {len(stocks)}")
    
    # 提取唯一商品
    unique = {}
    for item in stocks:
        nm_id = item.get("nmId")
        if nm_id and nm_id not in unique:
            unique[nm_id] = {
                "nmId": nm_id,
                "article": item.get("supplierArticle"),
                "barcode": item.get("barcode"),
            }
    
    print(f"唯一商品数: {len(unique)}")
    print("\n前5个商品:")
    for i, (nm_id, prod) in enumerate(list(unique.items())[:5]):
        print(f"  {i+1}. nmId: {nm_id}, article: {prod.get('article')}")
else:
    print(f"错误: {resp.status_code} - {resp.text[:100]}")

client.close()
