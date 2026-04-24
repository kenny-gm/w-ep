#!/usr/bin/env python3
"""检查CPM广告"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

headers = {"Authorization": shop.api_token}
client = httpx.Client(timeout=30)

# 获取广告列表
resp = client.get("https://advert-api.wildberries.ru/api/advert/v2/adverts", headers=headers)
data = resp.json()
adverts = data.get("adverts", [])

# 统计不同类型的广告
cpm_ads = []
cpc_ads = []

for ad in adverts:
    payment_type = ad.get("settings", {}).get("payment_type", "")
    if payment_type == "cpm":
        cpm_ads.append(ad.get("id"))
    elif payment_type == "cpc":
        cpc_ads.append(ad.get("id"))

print(f"CPM广告数量: {len(cpm_ads)}")
print(f"CPC广告数量: {len(cpc_ads)}")
print(f"CPM广告IDs: {cpm_ads[:5]}")

db.close()
