#!/usr/bin/env python3
"""测试正确的广告统计API"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop
from datetime import datetime, timedelta

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

headers = {"Authorization": shop.api_token, "Content-Type": "application/json"}
client = httpx.Client(timeout=30)

# 1. 获取广告列表
print("=== 1. 获取广告列表 ===")
resp = client.get("https://advert-api.wildberries.ru/api/advert/v2/adverts", headers=headers)
data = resp.json()
adverts = data.get("adverts", [])
print(f"广告数量: {len(adverts)}")

# 获取前3个广告ID
ad_ids = [ad.get("id") for ad in adverts[:3]]
print(f"测试广告IDs: {ad_ids}")

# 2. 获取广告统计 v3
print("\n=== 2. 获取广告统计 (v3/fullstats) ===")
date_to = datetime.now().strftime("%Y-%m-%d")
date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
ids_str = ",".join(map(str, ad_ids))

url = f"https://advert-api.wildberries.ru/adv/v3/fullstats?ids={ids_str}&beginDate={date_from}&endDate={date_to}"
print(f"请求: {url}")
resp = client.get(url, headers=headers)
print(f"状态: {resp.status_code}")

if resp.status_code == 200:
    stats = resp.json()
    print(f"响应类型: {type(stats)}")
    if isinstance(stats, list):
        print(f"记录数: {len(stats)}")
        if stats:
            print(f"第一条: {stats[0]}")
    else:
        print(f"响应: {stats}")
else:
    print(f"错误: {resp.text[:200]}")

db.close()
