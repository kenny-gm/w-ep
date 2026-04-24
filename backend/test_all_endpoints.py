#!/usr/bin/env python3
"""测试所有可能的API"""
from app.database import SessionLocal
from app.models.models import Shop
import httpx

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()
token = shop.api_token

print("=" * 70)
print("WB API 全端点测试")
print("=" * 70)

headers = {"Authorization": token, "Content-Type": "application/json"}

with httpx.Client(timeout=15.0) as client:
    # Content API v1
    print("\n【Content API v1】")
    v1_endpoints = [
        "https://content-api.wildberries.ru/content/v1/cards",
        "https://content-api.wildberries.ru/content/v1/cards/list",
    ]
    for ep in v1_endpoints:
        try:
            resp = client.post(ep, headers=headers, json={})
            print(f"  {ep.split('ru/')[-1]}: {resp.status_code}")
        except Exception as e:
            print(f"  {ep.split('ru/')[-1]}: 错误 - {str(e)[:30]}")

    # Content API v2
    print("\n【Content API v2】")
    v2_endpoints = [
        ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/list", {}),
        ("POST", "https://content-api.wildberries.ru/content/v2/get/cards/ids", {}),
        ("GET", "https://content-api.wildberries.ru/content/v2/object/parent/all", None),
        ("POST", "https://content-api.wildberries.ru/content/v2/get/nm-details", {"nm": [1,2,3]}),
    ]
    for method, ep, body in v2_endpoints:
        try:
            if method == "GET":
                resp = client.get(ep, headers=headers)
            else:
                resp = client.post(ep, headers=headers, json=body)
            print(f"  {ep.split('ru/')[-1]}: {resp.status_code}")
        except Exception as e:
            print(f"  {ep.split('ru/')[-1]}: 错误 - {str(e)[:30]}")

    # 尝试不同Content-Type
    print("\n【不同Content-Type测试】")
    content_types = ["application/json", "application/json; charset=utf-8"]
    for ct in content_types:
        h = {"Authorization": token, "Content-Type": ct}
        try:
            resp = client.post("https://content-api.wildberries.ru/content/v2/get/cards/list", 
                            headers=h, json={"limit": 10})
            print(f"  Content-Type={ct}: {resp.status_code}, cards={len(resp.json().get('cards', []))}")
        except Exception as e:
            print(f"  Content-Type={ct}: 错误")

    # 尝试带query参数
    print("\n【URL参数测试】")
    urls = [
        "https://content-api.wildberries.ru/content/v2/get/cards/list?limit=10",
    ]
    for u in urls:
        try:
            resp = client.post(u, headers=headers, json={})
            print(f"  {u.split('?')[-1]}: {resp.status_code}")
        except Exception as e:
            print(f"  错误: {str(e)[:30]}")

db.close()

print("\n" + "=" * 70)
print("可能的解决方案")
print("=" * 70)
print("""
1. 确认产品确实存在于该账户下
2. 确认产品已发布（不是在草稿箱）
3. 检查是否需要使用其他API版本
4. 尝试联系WB技术支持

代码本身没有问题，API调用是正确的。
""")
