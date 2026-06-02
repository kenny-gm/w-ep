#!/usr/bin/env python3
"""测试 businessId 级别 shows-sales 请求"""
import sys
sys.path.insert(0, "/app/backend")

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def test_business_traffic():
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

        config = shop.platform_config or {}
        business_id = config.get("business_id")
        logger.info(f"Testing businessId approach. business_id={business_id}")
        logger.info(f"platform_config: {config}")

        service = SyncService(db, shop)
        
        # 测试单日 2026-06-01
        result = service.sync_yandex_traffic(
            date_from="2026-06-01",
            date_to="2026-06-01"
        )
        logger.info(f"traffic result: {result}")

        # 验证
        rows = db.execute(text("""
            SELECT ar.product_id, p.sku, ar.order_count, ar.sales, ar.visitors, ar.impressions
            FROM ad_records ar
            JOIN products p ON ar.product_id = p.id
            WHERE ar.shop_id=5 AND ar.ad_type='product_analytics' AND DATE(ar.record_date)='2026-06-01'
            ORDER BY ar.visitors DESC LIMIT 5
        """)).fetchall()
        logger.info("\n=== 6/1 流量验证 ===")
        for r in rows:
            logger.info(f"  sku={r[1]} visitors={r[4]} impressions={r[5]} order_count={r[2]}")

    finally:
        db.close()

if __name__ == "__main__":
    test_business_traffic()