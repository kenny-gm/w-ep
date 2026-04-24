#!/usr/bin/env python3
"""测试v3/fullstats并解析数据"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop
from datetime import datetime, timedelta

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

headers = {"Authorization": shop.api_token}
client = httpx.Client(timeout=30)

# 获取广告列表
resp = client.get("https://advert-api.wildberries.ru/api/advert/v2/adverts", headers=headers)
data = resp.json()
adverts = data.get("adverts", [])
print(f"广告数量: {len(adverts)}")

# 获取第一个广告的ID和nm_id
if adverts:
    ad = adverts[0]
    ad_id = ad.get("id")
    nm_ids = [nm.get("nm_id") for nm in ad.get("nm_settings", [])]
    print(f"\n第一个广告: id={ad_id}, nm_ids={nm_ids}")
    
    # 测试广告统计
    date_to = datetime.now().strftime("%Y-%m-%d")
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    url = f"https://advert-api.wildberries.ru/adv/v3/fullstats?ids={ad_id}&beginDate={date_from}&endDate={date_to}"
    resp = client.get(url, headers=headers)
    print(f"\n广告统计状态: {resp.status_code}")
    
    if resp.status_code == 200:
        stats = resp.json()
        print(f"统计记录数: {len(stats)}")
        if stats:
            stat = stats[0]
            print(f"advertId: {stat.get('advertId')}")
            print(f"views: {stat.get('views')}, clicks: {stat.get('clicks')}, sum: {stat.get('sum')}")
            
            # 检查days
            days = stat.get("days", [])
            print(f"天数: {len(days)}")
            if days:
                print(f"第一天: {days[0]}")

db.close()
