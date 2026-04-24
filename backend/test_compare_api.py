#!/usr/bin/env python3
"""对比测试：广告 vs 商品"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token
db.close()

headers = {"Authorization": token, "Content-Type": "application/json"}
client = httpx.Client(timeout=15)

print("=" * 70)
print("对比测试：广告 vs 商品")
print("=" * 70)

# 1. 广告API
print("\n【广告API】")
resp = client.get("https://advert-api.wildberries.ru/api/advert/v2/adverts", headers=headers)
print(f"状态: {resp.status_code}")
adverts = []
if resp.status_code == 200:
    data = resp.json()
    adverts = data.get("adverts", [])
    print(f"✅ 成功! 广告数量: {len(adverts)}")
    if adverts:
        first = adverts[0]
        nm_settings = first.get("nm_settings", [])
        if nm_settings:
            nm_id = nm_settings[0].get("nm_id")
            print(f"   第一个广告的nm_id: {nm_id}")

# 2. Content API
print("\n【Content API】")
resp = client.post("https://content-api.wildberries.ru/content/v2/get/cards/list",
                   headers=headers, json={"limit": 10})
print(f"状态: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    cards = data.get("cards", [])
    total = data.get("cursor", {}).get("total", 0)
    print(f"❌ cards={len(cards)}, total={total}")

# 3. 用广告的nm_id查询
print("\n【用广告的nm_id查询商品】")
if adverts:
    nm_settings = adverts[0].get("nm_settings", [])
    if nm_settings:
        nm_id = nm_settings[0].get("nm_id")
        print(f"查询nm_id: {nm_id}")
        resp = client.post("https://content-api.wildberries.ru/content/v2/get/cards/list",
                           headers=headers, json={"nmId": nm_id})
        data = resp.json()
        cards = data.get("cards", [])
        print(f"状态: {resp.status_code}, cards: {len(cards)}")
        if cards:
            print(f"✅ 找到商品!")
            print(f"   vendorCode: {cards[0].get('vendorCode')}")
            print(f"   object: {cards[0].get('object')}")
        else:
            print(f"❌ 未找到商品")

client.close()
