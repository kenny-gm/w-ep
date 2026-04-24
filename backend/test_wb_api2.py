#!/usr/bin/env python3
"""解码JWT Token并测试其他API"""
import httpx
import json
import base64
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 6).first()

if shop and shop.api_token:
    token = shop.api_token
    
    # 解码JWT Token
    print("="*60)
    print("JWT Token 信息:")
    print("="*60)
    try:
        # JWT格式: header.payload.signature
        parts = token.split('.')
        if len(parts) == 3:
            # 解码payload
            payload = parts[1]
            # 添加padding
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.b64decode(payload)
            payload_data = json.loads(decoded)
            print(json.dumps(payload_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"解码失败: {e}")
    
    # 测试其他API
    print("\n" + "="*60)
    print("测试其他API端点:")
    print("="*60)
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    # 测试获取类目
    print("\n1. 测试获取类目 (parent/all):")
    try:
        url = "https://content-api.wildberries.ru/content/v2/object/parent/all"
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            print(f"状态码: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"类目数量: {len(data) if isinstance(data, list) else 'N/A'}")
            else:
                print(f"响应: {resp.text[:200]}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试订单API
    print("\n2. 测试订单API:")
    try:
        url = "https://marketplace-api.wildberries.ru/api/v3/orders/new"
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            print(f"状态码: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                orders = data.get('orders', [])
                print(f"新订单数量: {len(orders)}")
            else:
                print(f"响应: {resp.text[:200]}")
    except Exception as e:
        print(f"错误: {e}")
    
    # 测试仓库API
    print("\n3. 测试仓库API:")
    try:
        url = "https://marketplace-api.wildberries.ru/api/v3/warehouses"
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            print(f"状态码: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"仓库数据: {json.dumps(data[:2] if isinstance(data, list) and len(data) > 0 else data, indent=2, ensure_ascii=False)[:300]}")
            else:
                print(f"响应: {resp.text[:200]}")
    except Exception as e:
        print(f"错误: {e}")

db.close()
