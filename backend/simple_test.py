#!/usr/bin/env python3
"""简单调试 - 只测试核心API"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token if shop else None
db.close()

print(f"Token长度: {len(token) if token else 0}")

# 测试Content API
url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
headers = {"Authorization": token, "Content-Type": "application/json"}

with httpx.Client(timeout=15.0) as client:
    # 测试1: 最简单请求
    resp = client.post(url, headers=headers, json={})
    print(f"\n测试1 - 空body:")
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text[:300]}")
    
    # 测试2: 带limit
    resp = client.post(url, headers=headers, json={"limit": 10})
    print(f"\n测试2 - limit=10:")
    print(f"状态码: {resp.status_code}")
    data = resp.json()
    print(f"cards: {len(data.get('cards', []))}")
    print(f"cursor: {data.get('cursor')}")
