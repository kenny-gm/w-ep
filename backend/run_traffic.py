#!/usr/bin/env python3
"""补跑 traffic 流量数据（不覆盖 order_count/sales）"""
import sys
sys.path.insert(0, "/app/backend")

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def run_traffic(days: int = 7):
    from app.database import SessionLocal
    from app.models.models import Shop
    from app.services.sync_fixed import SyncService
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo

    db = SessionLocal()
    try:
        shop = db.query(Shop).filter(Shop.id == 5).first()
        if not shop:
            logger.error("Shop 5 not found")
            return

        tz = ZoneInfo("Asia/Shanghai")
        end_date = datetime.now(tz).strftime("%Y-%m-%d")
        start_date = (datetime.now(tz) - timedelta(days=days)).strftime("%Y-%m-%d")

        logger.info(f"补跑 traffic，shop={shop.name}, days={days}, {start_date} to {end_date}")
        service = SyncService(db, shop)
        result = service.sync_yandex_traffic(date_from=start_date, date_to=end_date)
        logger.info(f"traffic result: {result}")

        # 验证流量字段是否写入
        from sqlalchemy import text
        rows = db.execute(text("""
            SELECT ar.product_id, p.sku, ar.order_count, ar.sales, ar.visitors, ar.impressions, ar.cart_count
            FROM ad_records ar
            JOIN products p ON ar.product_id = p.id
            WHERE ar.shop_id=5 AND ar.ad_type='product_analytics' AND DATE(ar.record_date)='2026-06-01'
            ORDER BY ar.visitors DESC LIMIT 5
        """)).fetchall()
        logger.info("\n=== 6/1 流量验证 ===")
        for r in rows:
            logger.info(f"  sku={r[1]} visitors={r[4]} impressions={r[5]} cart_count={r[6]} order_count={r[2]}")

    finally:
        db.close()

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    run_traffic(days)