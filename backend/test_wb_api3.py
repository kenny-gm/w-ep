#!/usr/bin/env python3
"""测试所有产品相关的API端点"""
import httpx
import json
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 6).first()

if shop and shop.api_token:
    token = shop.api_token
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    print("="*60)
    print(f"店铺ID (oid): 250042561")
    print("="*60)
    
    # 测试不同的产品API端点
    endpoints = [
        # Content API - 卡片列表
        {
            "name": "1. Content API - 卡片列表 (v2)",
            "method": "POST",
            "url": "https://content-api.wildberries.ru/content/v2/get/cards/list",
            "body": {"limit": 100}
        },
        # Content API - 卡片列表 (v1)
        {
            "name": "2. Content API - 卡片列表 (v1)",
            "method": "POST",
            "url": "https://content-api.wildberries.ru/content/v1/cards/list",
            "body": {"limit": 100}
        },
        # Content API - 卡片筛选
        {
            "name": "3. Content API - 卡片筛选 (filter)",
            "method": "POST",
            "url": "https://content-api.wildberries.ru/content/v2/get/cards/filter",
            "body": {"limit": 100}
        },
        # Marketplace API - 产品列表
        {
            "name": "4. Marketplace API - 产品列表",
            "method": "GET",
            "url": "https://marketplace-api.wildberries.ru/api/v3/items",
            "body": None
        },
        # Stats API - 产品统计
        {
            "name": "5. Stats API - 产品统计",
            "method": "POST",
            "url": "https://statistics-api.wildberries.ru/api/v1/supplier/incomes",
            "body": {"dateFrom": "2026-03-01"}
        },
        # Analytics API - 产品报告
        {
            "name": "6. Analytics API - nm-report",
            "method": "POST",
            "url": "https://seller-analytics-api.wildberries.ru/api/v2/nm-report",
            "body": {
                "period": {"begin": "2026-03-01", "end": "2026-03-20"},
                "brandNames": [],
                "objectIDs": [],
                "nmIDs": []
            }
        },
        # Content API - 草稿
        {
            "name": "7. Content API - 草稿列表",
            "method": "GET",
            "url": "https://content-api.wildberries.ru/content/v2/drafts/list",
            "body": None
        },
    ]
    
    for ep in endpoints:
        print(f"\n{ep['name']}")
        print(f"URL: {ep['url']}")
        try:
            with httpx.Client(timeout=15.0) as client:
                if ep["method"] == "POST":
                    resp = client.post(ep["url"], headers=headers, json=ep.get("body"))
                else:
                    resp = client.get(ep["url"], headers=headers)
                
                print(f"状态码: {resp.status_code}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    # 检查是否有产品数据
                    if "cards" in data:
                        print(f"✅ cards数量: {len(data.get('cards', []))}")
                        if data.get('cards'):
                            print(f"第一个: {data['cards'][0]}")
                    elif "items" in data:
                        print(f"✅ items数量: {len(data.get('items', []))}")
                        if data.get('items'):
                            print(f"第一个: {data['items'][0]}")
                    elif "data" in data:
                        d = data.get('data', {})
                        if isinstance(d, list):
                            print(f"✅ data数量: {len(d)}")
                        elif isinstance(d, dict):
                            if 'cards' in d:
                                print(f"✅ data.cards数量: {len(d.get('cards', []))}")
                            elif 'products' in d:
                                print(f"✅ data.products数量: {len(d.get('products', []))}")
                            else:
                                print(f"✅ data keys: {list(d.keys())[:10]}")
                    elif isinstance(data, list):
                        print(f"✅ 列表数量: {len(data)}")
                        if data:
                            print(f"第一个: {data[0]}")
                    else:
                        print(f"响应keys: {list(data.keys())[:10]}")
                        print(f"响应预览: {json.dumps(data, ensure_ascii=False)[:300]}")
                elif resp.status_code == 401:
                    print(f"❌ 未授权")
                elif resp.status_code == 403:
                    print(f"❌ 无权限")
                else:
                    print(f"响应: {resp.text[:200]}")
        except Exception as e:
            print(f"❌ 错误: {e}")

db.close()
