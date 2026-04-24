"""
主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base

# 导入路由
from app.routers import auth, dashboard, products, shops, admin, users, inventory, orders, ads, finance, profit
from app.routers import metric_thresholds
from app.routers import ai_config
from app.routers import alerts, operation_logs, effect_analysis

# 导入所有模型（确保create_all能创建所有表）
from app.models.models import (
    User, Shop, Product, ProductPermission, InventoryRecord, InventorySnapshot,
    Order, OrderItem, AdRecord, SystemSetting, UISetting, MenuItem, SyncLog,
    MetricHistory, OperationLog, Alert, AlertRule
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Wildberries 跨境电商 ERP 系统"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(products.router)
app.include_router(shops.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(ads.router)
app.include_router(profit.router)
app.include_router(finance.router)
app.include_router(metric_thresholds.router)
app.include_router(ai_config.router)
app.include_router(alerts.router)
app.include_router(operation_logs.router)
app.include_router(effect_analysis.router)


@app.get("/")
def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """启动时初始化"""
    try:
        from app.tasks.scheduler import start_scheduler
        start_scheduler()
        print("定时任务调度器已启动")
    except Exception as e:
        print(f"启动定时任务失败: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
