#!/usr/bin/env python3
"""测试Product Cards API - 根据官方文档"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token
db.close()

headers = {"Authorization": token, "Content-Type": "application/json"}

print("测试 /content/v2/get/cards/list")
with httpx.Client(timeout=10) as client:
    # 测试1: 空请求
    resp = client.post(
        "https://content-api.wildberries.ru/content/v2/get/cards/list",
        headers=headers,
        json={}
    )
    print(f"状态: {resp.status_code}")
    data = resp.json()
    print(f"cards: {len(data.get('cards', []))}")
    print(f"cursor: {data.get('cursor')}")

    # 测试2: limit=10
    resp = client.post(
        "https://content-api.wildberries.ru/content/v2/get/cards/list",
        headers=headers,
        json={"limit": 10}
    )
    data = resp.json()
    print(f"\nlimit=10: cards={len(data.get('cards', []))}")
