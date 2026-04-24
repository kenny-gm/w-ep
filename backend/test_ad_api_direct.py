#!/usr/bin/env python3
"""直接测试广告API"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

print(f"Token: {shop.api_token[:50]}...")

headers = {"Authorization": shop.api_token}
client = httpx.Client(timeout=30, follow_redirects=True)

# 测试1: 直接用httpx
print("\n=== 测试1: 直接httpx ===")
resp = client.get("https://advert-api.wildberries.ru/api/advert/v2/adverts", headers=headers)
print(f"状态: {resp.status_code}")
print(f"响应: {resp.text[:300] if resp.text else 'empty'}")

db.close()
