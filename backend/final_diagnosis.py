#!/usr/bin/env python3
"""最终诊断"""
from app.database import SessionLocal
from app.models.models import Shop
import httpx
import json

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token

print("=" * 70)
print("最终诊断")
print("=" * 70)

print(f"\n店铺: {shop.name}")
print(f"Token长度: {len(token)}")
print(f"Token前50: {token[:50]}")

# 测试API
headers = {"Authorization": token, "Content-Type": "application/json"}
url = "https://content-api.wildberries.ru/content/v2/get/cards/list"

print(f"\n请求URL: {url}")
print("请求Body: {}")

with httpx.Client(timeout=15) as client:
    resp = client.post(url, headers=headers, json={})
    data = resp.json()

    print(f"\n响应状态: {resp.status_code}")
    print(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")

    cards = data.get("cards", [])
    cursor = data.get("cursor", {})

    print(f"\n结果:")
    print(f"  cards数量: {len(cards)}")
    print(f"  total: {cursor.get('total', 0)}")
    print(f"  nmID: {cursor.get('nmID', 0)}")

    if resp.status_code == 200 and len(cards) == 0:
        print("\n" + "=" * 70)
        print("结论: API调用成功，但WB后台没有返回任何产品数据")
        print("=" * 70)
        print("""
可能原因:
1. 该账户下确实没有产品
2. 产品在审核中/未发布
3. 产品在其他组织/账户下
4. WB API问题

建议:
1. 登录WB后台确认产品状态
2. 检查账户ID和组织ID是否匹配
3. 确认产品已上架
        """)
    elif resp.status_code != 200:
        print("\n" + "=" * 70)
        print("结论: API调用失败")
        print("=" * 70)
        print(f"错误: {data}")

db.close()
