#!/usr/bin/env python3
"""
历史回填脚本：按新口径（精确状态过滤）重新计算 Yandex AdRecord.order_count/sales

重新从 stats/orders API 获取数据，按新过滤规则（精确匹配 + PAYMENT优先）重新聚合，
然后更新 shop_id=5 的 AdRecord(product_analytics) 记录。

用法：
  python3 scripts/backfill_yandex_orders.py [days=60]
"""
import sys
import os
sys.path.insert(0, "/app")

from datetime import datetime, timedelta, ZoneInfo
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def backfill_yandex_orders(days: int = 60):
    from app.database import SessionLocal
    from app.models.models import Shop, AdRecord
    from app.services.sync_fixed import YandexSyncService

    db = SessionLocal()
    try:
        shop = db.query(Shop).filter(Shop.id == 5).first()
        if not shop:
            logger.error("Shop 5 not found")
            return

        logger.info(f"开始回填 Yandex orders，shop={shop.name}, days={days}")

        service = YandexSyncService(db, shop)

        tz = ZoneInfo("Asia/Shanghai")
        end_date = datetime.now(tz).strftime("%Y-%m-%d")
        start_date = (datetime.now(tz) - timedelta(days=days)).strftime("%Y-%m-%d")

        logger.info(f"date range: {start_date} to {end_date}")

        result = service.sync_yandex_orders(days=days)
        logger.info(f"sync_yandex_orders result: {result}")

        # 验证回填结果
        updated_count = db.execute(
            f"SELECT COUNT(*) FROM ad_records WHERE shop_id=5 AND ad_type='product_analytics'"
        ).fetchone()[0]
        logger.info(f"回填后 AdRecord 总数: {updated_count}")

    finally:
        db.close()

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    backfill_yandex_orders(days)