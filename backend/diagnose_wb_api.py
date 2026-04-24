#!/usr/bin/env python3
"""
深度测试WB API - 找出产品为0的真正原因
"""
import httpx
import json
import base64
from app.database import SessionLocal
from app.models.models import Shop

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token if shop else None
db.close()

if not token:
    print("❌ 没有Token")
    exit()

print("="*70)
print("WB API 深度诊断")
print("="*70)

# 解码JWT
print("\n【1】JWT Token 信息:")
parts = token.split('.')
if len(parts) == 3:
    payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
    decoded = json.loads(base64.b64decode(payload))
    print(f"UID (用户ID): {decoded.get('uid')}")
    print(f"OID (组织ID): {decoded.get('oid')}")
    print(f"过期时间: {decoded.get('exp')}")
    print(f"用途: {decoded.get('for')}")

headers = {"Authorization": token, "Content-Type": "application/json"}

# 测试基础API
print("\n【2】测试基础API:")
test_apis = [
    ("卖家信息", "GET", "https://common-api.wildberries.ru/api/v1/seller-info"),
    ("仓库列表", "GET", "https://marketplace-api.wildberries.ru/api/v3/warehouses"),
    ("新订单", "GET", "https://marketplace-api.wildberries.ru/api/v3/orders/new"),
]

with httpx.Client(timeout=15.0) as client:
    for name, method, url in test_apis:
        try:
            resp = client.get(url, headers=headers) if method == "GET" else client.post(url, headers=headers, json={})
            print(f"\n{name}:")
            print(f"  状态码: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    print(f"  ✅ 返回 {len(data)} 条记录")
                elif isinstance(data, dict):
                    print(f"  ✅ 返回字段: {list(data.keys())[:5]}")
            else:
                print(f"  ❌ {resp.text[:100]}")
        except Exception as e:
            print(f"  ❌ 错误: {e}")

# 测试Content API - 不同参数
print("\n【3】测试Content API (不同参数组合):")
content_tests = [
    {"limit": 100},
    {"limit": 100, "offset": 0},
    {"limit": 100, "locale": "ru"},
    {"limit": 100, "locale": "zh"},
    {"limit": 100, "withPhoto": True},
    {"limit": 100, "withPhoto": False},
]

url = "https://content-api.wildberries.ru/content/v2/get/cards/list"
with httpx.Client(timeout=15.0) as client:
    for body in content_tests:
        try:
            resp = client.post(url, headers=headers, json=body)
            data = resp.json()
            cards = data.get('cards', [])
            total = data.get('cursor', {}).get('total', 0)
            print(f"  {body} → cards: {len(cards)}, total: {total}")
        except Exception as e:
            print(f"  {body} → 错误: {e}")

# 测试是否是沙箱环境
print("\n【4】检查环境:")
print(f"  Token长度: {len(token)}")
print(f"  Token格式: {'JWT' if '.' in token else 'API Key'}")

# 测试其他可能的产品API
print("\n【5】测试其他产品相关API:")
other_apis = [
    ("产品统计", "POST", "https://seller-analytics-api.wildberries.ru/api/v2/nm-report", 
     {"period": {"begin": "2026-03-01", "end": "2026-03-20"}, "nmIDs": [], "brandNames": [], "objectIDs": []}),
    ("销售历史", "POST", "https://seller-analytics-api.wildberries.ru/api/analytics/v3/sales-funnel/products/history",
     {"period": {"begin": "2026-03-01", "end": "2026-03-20"}}),
    ("入库单", "POST", "https://statistics-api.wildberries.ru/api/v1/supplier/incomes",
     {"dateFrom": "2026-03-01"}),
    ("库存报表", "POST", "https://statistics-api.wildberries.ru/api/v1/supplier/stocks",
     {"dateFrom": "2026-03-20"}),
]

with httpx.Client(timeout=15.0) as client:
    for name, method, url, body in other_apis:
        try:
            resp = client.post(url, headers=headers, json=body)
            print(f"\n  {name}:")
            print(f"    状态码: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    print(f"    ✅ {len(data)} 条记录")
                elif isinstance(data, dict):
                    keys = list(data.keys())
                    print(f"    ✅ 返回字段: {keys[:5]}")
                    # 检查是否有产品数据
                    if 'cards' in data:
                        print(f"    产品数量: {len(data.get('cards', []))}")
                    if 'products' in data:
                        print(f"    产品数量: {len(data.get('products', []))}")
            else:
                print(f"    ❌ {resp.text[:150]}")
        except Exception as e:
            print(f"    ❌ 错误: {str(e)[:100]}")

print("\n" + "="*70)
print("诊断完成")
print("="*70)
print("\n建议:")
print("1. 如果所有API都返回0，请检查:")
print("   - Token权限是否包含所有API")
print("   - WB后台是否切换到了正确的店铺")
print("   - 产品是否已发布（不只是草稿）")
print("\n2. 如果某些API有数据，某些没有:")
print("   - 可能是该API的权限问题")
print("   - 可能是该数据的创建时间问题")
