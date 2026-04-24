#!/usr/bin/env python3
"""测试WBAPIClient"""
import sys
sys.path.insert(0, '/app')

from app.database import SessionLocal
from app.models.models import Shop
from app.services.wb_api import WBAPIClient

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

print(f"创建API客户端...")
client = WBAPIClient(shop.api_token)

print(f"获取广告列表...")
adverts = client.get_adverts()
print(f"广告数量: {len(adverts)}")

if adverts:
    print(f"第一个广告: {adverts[0]}")

db.close()
