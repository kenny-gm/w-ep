from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

def start_scheduler():
    try:
        from app.tasks.metric_snapshot import daily_metric_snapshot
        from app.tasks.alert_engine import run_alert_engine
        from app.tasks.effect_tracking import track_operation_effects
        
        # Daily at 6 AM - metric snapshot
        scheduler.add_job(daily_metric_snapshot, CronTrigger(hour=6, minute=0))
        # Daily at 6:05 AM - generate alerts
        scheduler.add_job(run_alert_engine, CronTrigger(hour=6, minute=5))
        # Daily at 6:10 AM - track operation effects
        scheduler.add_job(track_operation_effects, CronTrigger(hour=6, minute=10))
        
        scheduler.start()
        print("定时任务调度器已启动")
    except Exception as e:
        print(f"启动定时任务失败: {e}")
