#!/usr/bin/env python3
"""Yandex 历史回填脚本 - 修复路径"""
import sys
sys.path.insert(0, "/app/backend")

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def backfill_yandex_orders(days: int = 7):
    from app.database import SessionLocal
    from app.models.models import Shop
    from app.services.sync_fixed import SyncService
    from sqlalchemy import text

    db = SessionLocal()
    try:
        shop = db.query(Shop).filter(Shop.id == 5).first()
        if not shop:
            logger.error("Shop 5 not found")
            return

        logger.info(f"开始回填 Yandex orders，shop={shop.name}, days={days}")

        service = SyncService(db, shop)

        result = service.sync_yandex_orders(days=days)
        logger.info(f"sync_yandex_orders result: {result}")

        # 验证回填结果
        updated_count = db.execute(
            text("SELECT COUNT(*) FROM ad_records WHERE shop_id=5 AND ad_type='product_analytics'")
        ).fetchone()[0]
        logger.info(f"回填后 AdRecord 总数: {updated_count}")

        # 抽查 6/1 和 5/31
        for target_date in ['2026-06-01', '2026-05-31']:
            logger.info(f"\n=== {target_date} 抽查 ===")
            rows = db.execute(text("""
                SELECT ar.product_id, p.sku, ar.order_count, ar.sales, ar.visitors, ar.impressions
                FROM ad_records ar
                JOIN products p ON ar.product_id = p.id
                WHERE ar.shop_id=5 AND ar.ad_type='product_analytics' AND DATE(ar.record_date)=:dt
                ORDER BY ar.order_count DESC LIMIT 10
            """), {"dt": target_date}).fetchall()
            for r in rows:
                logger.info(f"  product_id={r[0]} sku={r[1]} order_count={r[2]} sales={r[3]:.2f} visitors={r[4]} impressions={r[5]}")
            if not rows:
                logger.info(f"  无记录")

    finally:
        db.close()

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    backfill_yandex_orders(days)