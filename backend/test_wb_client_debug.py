#!/usr/bin/env python3
"""调试WBAPIClient"""
import sys
import httpx
sys.path.insert(0, '/app')

from app.database import SessionLocal
from app.models.models import Shop
from app.services.wb_api import WBAPIClient, RateLimiter

db = SessionLocal()
shop = db.query(Shop).filter(Shop.id == 2).first()

# 手动测试
print("=== 手动测试 ===")
client = httpx.Client(timeout=30)
headers = {"Authorization": shop.api_token}
resp = client.get("https://advert-api.wildberries.ru/api/advert/v2/adverts", headers=headers)
print(f"状态: {resp.status_code}")
data = resp.json()
print(f"adverts: {len(data.get('adverts', []))}")

# 通过WBAPIClient测试
print("\n=== WBAPIClient测试 ===")
wb_client = WBAPIClient(shop.api_token)
print(f"headers: {wb_client.headers}")
print(f"API_DOMAINS: {wb_client.API_DOMAINS}")

# 打印_rate_limits
print(f"RATE_LIMITS keys: {list(wb_client.RATE_LIMITS.keys())}")

# 直接调用_request
print("\n=== 直接调用_request ===")
try:
    result = wb_client._request("GET", "promotion", "/api/advert/v2/adverts")
    print(f"结果: {result}")
    print(f"结果类型: {type(result)}")
    if isinstance(result, dict):
        print(f"adverts数量: {len(result.get('adverts', []))}")
except Exception as e:
    print(f"错误: {e}")

db.close()
