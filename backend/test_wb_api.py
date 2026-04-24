#!/usr/bin/env python3
"""测试WB Content API"""
import httpx
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 6).first()

if shop and shop.api_token:
    token = shop.api_token
    url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    print(f"Token长度: {len(token)}")
    print(f"Token前50位: {token[:50]}")
    
    # 测试不同请求
    tests = [
        {"locale": "ru"},
        {"limit": 10},
        {"locale": "ru", "limit": 10, "offset": 0},
        {},
        {"locale": "zh"},
    ]
    
    for i, body in enumerate(tests):
        print(f"\n{'='*50}")
        print(f"测试{i+1}: {body}")
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, headers=headers, json=body)
                print(f"状态码: {resp.status_code}")
                data = resp.json()
                if "cards" in data:
                    cards = data.get('cards', [])
                    total = data.get('cursor', {}).get('total', 0)
                    print(f"✅ 产品数量: {len(cards)}")
                    print(f"✅ Total: {total}")
                    if cards:
                        print(f"第一个产品: {cards[0]}")
                else:
                    print(f"响应: {resp.text[:300]}")
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
else:
    print("店铺不存在或没有Token")

db.close()
