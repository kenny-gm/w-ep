#!/usr/bin/env python3
"""解析所有店铺的Token"""
from app.database import SessionLocal
from app.models.models import Shop
import json
import base64

db = SessionLocal()

print("=" * 70)
print("WB Token ID 解析")
print("=" * 70)

for shop in db.query(Shop).all():
    token = shop.api_token
    if not token or len(token) < 100:
        print(f"\n【店铺: {shop.name}】")
        print(f"  ERP店铺ID: {shop.id}")
        print(f"  Token: 无或过短")
        continue

    print(f"\n【店铺: {shop.name}】")
    print(f"  ERP店铺ID: {shop.id}")

    # 解析JWT
    parts = token.split(".")
    if len(parts) >= 2:
        payload_data = parts[1] + "=" * (4 - len(parts[1]) % 4)
        try:
            payload = json.loads(base64.b64decode(payload_data))
            uid = payload.get("uid", "N/A")
            oid = payload.get("oid", "N/A")
            acc = payload.get("acc", "N/A")
            exp = payload.get("exp", "N/A")

            print(f"  用户ID (uid): {uid}")
            print(f"  组织ID (oid): {oid}")
            print(f"  权限 (acc): {acc}")
            if exp != "N/A":
                import time
                exp_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))
                print(f"  过期时间: {exp_time}")

            print(f"\n  说明:")
            print(f"    - uid: WB账户的用户ID")
            print(f"    - oid: WB的组织/商户ID（不是店铺ID）")
            print(f"    - WB系统可能一个组织下有多个店铺")
        except Exception as e:
            print(f"  解析错误: {e}")

db.close()
