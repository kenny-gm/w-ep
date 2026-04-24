#!/usr/bin/env python3
"""
逐行检查并测试WB API调用
"""
import httpx
import json
import base64
from app.database import SessionLocal
from app.models.models import Shop

# 1. 获取Token
print("="*70)
print("步骤1: 获取Token")
print("="*70)
db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
if not shop:
    print("❌ 店铺不存在")
    exit()
token = shop.api_token
print(f"✅ 店铺: {shop.name}")
print(f"✅ Token长度: {len(token) if token else 0}")

if not token:
    print("❌ 没有Token")
    exit()

# 2. 解析JWT
print("\n" + "="*70)
print("步骤2: 解析JWT Token")
print("="*70)
parts = token.split('.')
if len(parts) >= 2:
    payload = parts[1]
    payload += '=' * (4 - len(payload) % 4)
    try:
        decoded = json.loads(base64.b64decode(payload))
        print(f"用户ID (uid): {decoded.get('uid')}")
        print(f"组织ID (oid): {decoded.get('oid')}")
    except Exception as e:
        print(f"解析JWT失败: {e}")

# 3. 构建请求
print("\n" + "="*70)
print("步骤3: 构建API请求")
print("="*70)
url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}
print(f"URL: {url}")
print(f"Headers: Authorization={token[:20]}...")

# 4. 测试不同的请求体
print("\n" + "="*70)
print("步骤4: 测试不同请求体")
print("="*70)

test_bodies = [
    # 标准请求
    {"limit": 100, "offset": 0, "locale": "ru"},
    
    # 最小请求
    {"limit": 10},
    
    # 带过滤
    {"limit": 10, "filter": {"withPhoto": True}},
    
    # 带排序
    {"limit": 10, "sort": {"column": "createdAt", "order": "desc"}},
]

with httpx.Client(timeout=30.0, verify=True) as client:
    for i, body in enumerate(test_bodies):
        print(f"\n测试 {i+1}: {json.dumps(body, ensure_ascii=False)}")
        
        try:
            # 发送请求
            resp = client.post(url, headers=headers, json=body)
            
            print(f"状态码: {resp.status_code}")
            print(f"响应头: {dict(resp.headers)[:200] if resp.headers else 'N/A'}")
            
            if resp.status_code == 200:
                data = resp.json()
                cards = data.get('cards', [])
                cursor = data.get('cursor', {})
                
                print(f"✅ cards数量: {len(cards)}")
                print(f"✅ cursor: {json.dumps(cursor, ensure_ascii=False)}")
                
                # 如果有cards，打印第一个
                if cards:
                    print(f"\n第一个产品:")
                    first = cards[0]
                    print(f"  nmID: {first.get('nmID')}")
                    print(f"  vendorCode: {first.get('vendorCode')}")
                    print(f"  object: {first.get('object')}")
                    print(f"  完整数据: {json.dumps(first, ensure_ascii=False, indent=2)[:500]}")
            else:
                print(f"❌ 响应: {resp.text[:300]}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()

# 5. 测试其他端点
print("\n" + "="*70)
print("步骤5: 测试其他Content API端点")
print("="*70)

other_endpoints = [
    ("获取草稿", "POST", "https://content-api.wildberries.ru/content/v1/cards"),
    ("获取类目", "GET", "https://content-api.wildberries.ru/content/v2/object/parent/all"),
    ("获取特征", "GET", "https://content-api.wildberries.ru/content/v2/characteristics/list"),
]

with httpx.Client(timeout=30.0) as client:
    for name, method, endpoint in other_endpoints:
        print(f"\n{name}: {endpoint}")
        try:
            if method == "GET":
                resp = client.get(endpoint, headers=headers)
            else:
                resp = client.post(endpoint, headers=headers, json={})
            
            print(f"状态码: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    print(f"✅ 返回 {len(data)} 条")
                    if data:
                        print(f"第一条: {json.dumps(data[0], ensure_ascii=False)[:200]}")
                else:
                    print(f"✅ 返回: {json.dumps(data, ensure_ascii=False)[:200]}")
            else:
                print(f"响应: {resp.text[:150]}")
        except Exception as e:
            print(f"错误: {str(e)[:100]}")

# 6. 最终诊断
print("\n" + "="*70)
print("诊断结论")
print("="*70)
print("\n如果cards始终为0，可能原因：")
print("1. Token对应的账户下没有产品")
print("2. 产品在审核中或未发布")
print("3. Token权限不足（需要Content API权限）")
print("4. 账户切换错误")
print("\n建议：")
print("1. 确认WB后台是否在该账户下能看到产品")
print("2. 检查Token生成时是否勾选了Content API权限")
print("3. 尝试重新生成Token")

db.close()
