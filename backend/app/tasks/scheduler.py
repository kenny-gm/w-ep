from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

def start_scheduler():
    try:
        from app.tasks.metric_snapshot import daily_metric_snapshot
        from app.tasks.alert_engine import run_alert_engine
        from app.tasks.effect_tracking import track_operation_effects
        
        # Daily at 6 AM Beijing time - metric snapshot
        scheduler.add_job(daily_metric_snapshot, CronTrigger(hour=6, minute=0, timezone="Asia/Shanghai"))
        # Daily at 6:05 AM Beijing time - generate alerts
        scheduler.add_job(run_alert_engine, CronTrigger(hour=6, minute=5, timezone="Asia/Shanghai"))
        # Daily at 6:10 AM Beijing time - track operation effects
        scheduler.add_job(track_operation_effects, CronTrigger(hour=6, minute=10, timezone="Asia/Shanghai"))
        # Daily at 6:15 AM Beijing time - Yandex traffic sync (shows-sales)
        scheduler.add_job(sync_yandex_traffic_task, CronTrigger(hour=6, minute=15, timezone="Asia/Shanghai"))
        
        scheduler.start()
        print("定时任务调度器已启动")
    except Exception as e:
        print(f"启动定时任务失败: {e}")


def sync_yandex_traffic_task():
    """每天 6:15 北京时间同步 Yandex 流量数据（shows-sales 报告）"""
    from app.core.database import SessionLocal
    from app.services.sync_fixed import SyncService
    from app.models.models import Shop
    import logging

    logger = logging.getLogger("sync")
    db = SessionLocal()
    try:
        # 只同步 Yandex 店铺
        shops = db.query(Shop).filter(Shop.platform == "yandex", Shop.is_active == 1).all()
        for shop in shops:
            try:
                svc = SyncService(db, shop)
                result = svc.sync_yandex_traffic()
                logger.info(f"Yandex traffic sync [{shop.name}]: {result}")
            except Exception as e:
                logger.error(f"Yandex traffic sync [{shop.name}] 失败: {e}")
    finally:
        db.close()