#!/usr/bin/env python3
"""解析JWT Token权限"""
from app.database import SessionLocal
from app.models.models import Shop
import json
import base64

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token

print("=" * 70)
print("JWT Token 详细解析")
print("=" * 70)

# 解析JWT
parts = token.split('.')
if len(parts) >= 2:
    # Header
    header_data = parts[0] + '=' * (4 - len(parts[0]) % 4)
    try:
        header = json.loads(base64.b64decode(header_data))
        print("\n【Header】")
        for k, v in header.items():
            print(f"  {k}: {v}")
    except:
        pass

    # Payload
    payload_data = parts[1] + '=' * (4 - len(parts[1]) % 4)
    try:
        payload = json.loads(base64.b64decode(payload_data))
        print("\n【Payload】")
        for k, v in payload.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"解析错误: {e}")

    # 分析权限
    print("\n【权限分析】")
    if 'acc' in payload:
        acc = payload['acc']
        print(f"  acc字段值: {acc}")
        # acc可能的值：
        # 0 - 无权限
        # 1 - 只读
        # 2 - 读写
        # 3 - 完全权限
        if acc == 0:
            print("  ❌ 无权限")
        elif acc == 1:
            print("  ⚠️ 只读权限")
        elif acc == 2:
            print("  ✅ 读写权限")
        elif acc == 3:
            print("  ✅ 完全权限")
        else:
            print(f"  ⚠️ 未知权限值: {acc}")

    if 'ent' in payload:
        ent = payload['ent']
        print(f"  ent字段值: {ent}")

    if 'oid' in payload:
        print(f"  组织ID(oid): {payload['oid']}")

    if 'uid' in payload:
        print(f"  用户ID(uid): {payload['uid']}")

    if 'exp' in payload:
        import time
        exp_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payload['exp']))
        print(f"  过期时间: {exp_time}")

db.close()

print("\n" + "=" * 70)
print("结论")
print("=" * 70)
print("""
如果acc=3，说明Token有完整权限，但WB后台可能没有产品。
如果acc<3，说明Token权限不足，需要在WB后台重新生成Token并勾选所有权限。

请确认：
1. WB后台登录的账户ID是否与Token中的uid一致
2. WB后台的组织ID是否与Token中的oid一致
3. 产品是否在该组织下
""")
