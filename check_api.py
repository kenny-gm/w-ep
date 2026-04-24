import sys
sys.path.insert(0, "/app")
from app.services.wb_api import WBAPIClient
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    token = conn.execute(text("SELECT api_token FROM shops WHERE id=1")).fetchone()[0]
    nmids = [int(row[0]) for row in conn.execute(text("SELECT nm_id FROM products WHERE shop_id=1")).fetchall()]

client = WBAPIClient(token)

result_16 = client.get_product_sales_funnel(nmids, "2026-04-16", "2026-04-16")
orders_16 = sum(d.get("order_count", 0) for data in result_16.values() for d in data.values())
sum_16 = sum(d.get("order_sum", 0) for data in result_16.values() for d in data.values())

result_17 = client.get_product_sales_funnel(nmids, "2026-04-17", "2026-04-17")
orders_17 = sum(d.get("order_count", 0) for data in result_17.values() for d in data.values())
sum_17 = sum(d.get("order_sum", 0) for data in result_17.values() for d in data.values())

print("API 04-16:", orders_16, "orders,", sum_16, "CNY")
print("API 04-17:", orders_17, "orders,", sum_17, "CNY")
