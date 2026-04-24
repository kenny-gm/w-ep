#!/usr/bin/env python3
"""检查产品和广告的nm_id匹配"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop, Product
from app.services.wb_api import WBAPIClient

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
client = WBAPIClient(shop.api_token)

# 获取广告列表
adverts = client.get_adverts()
print(f"广告数量: {len(adverts)}")

# 获取所有nm_id
all_nm_ids = set()
for ad in adverts:
    for nm in ad.get("nm_settings", []):
        all_nm_ids.add(nm.get("nm_id"))

print(f"\n广告中的nm_id列表(前10):")
for nm_id in sorted(all_nm_ids)[:10]:
    print(f"  {nm_id}")

# 获取产品列表
products = db.query(Product).filter(Product.shop_id == 2).all()
print(f"\n产品中的nm_id列表(前10):")
for p in products[:10]:
    print(f"  产品{p.id}: nm_id={p.nm_id}")

# 检查是否有匹配
product_nm_ids = set(int(p.nm_id) for p in products)
matching = all_nm_ids & product_nm_ids
print(f"\n匹配的nm_id数量: {len(matching)}")
print(f"匹配的nm_id: {list(matching)}")

db.close()
