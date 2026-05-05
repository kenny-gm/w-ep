"""
WB ERP 配置文件
从环境变量读取配置，支持 .env 文件
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import os
from datetime import timezone, timedelta


class Settings(BaseSettings):
    # ========== 应用配置 ==========
    APP_NAME: str = "WB ERP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # ========== 时区配置 ==========
    TIMEZONE: str = "Asia/Shanghai"
    TZ: str = "Asia/Shanghai"
    
    # ========== 数据库配置 ==========
    DATABASE_URL: str = "sqlite:////app/db/wb_erp.db"
    
    # ========== JWT 配置 ==========
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1  # 1天
    
    # ========== WB API 配置 ==========
    WB_API_KEY: Optional[str] = None
    WB_API_TIMEOUT: int = 30
    WB_API_RETRY: int = 3
    WB_API_RATE_LIMIT_DELAY: float = 0.2
    
    # ========== 各分类限流配置 ==========
    WB_MARKETPLACE_LIMIT: int = 300
    WB_CONTENT_LIMIT: int = 300
    WB_ANALYTICS_LIMIT: int = 100
    WB_STATISTICS_LIMIT: int = 100
    WB_PROMOTION_LIMIT: int = 200
    WB_FINANCE_LIMIT: int = 60
    
    # ========== 同步配置 ==========
    SYNC_ENABLED: bool = True
    SYNC_INTERVAL_HOURS: int = 24
    SYNC_HOUR: int = 3
    
    # ========== 汇率配置 ==========
    DEFAULT_CNY_TO_RUB: float = 12.5
    
    # ========== 预警阈值 ==========
    AD_RATIO_WARNING: float = 0.03
    AD_RATIO_DANGER: float = 0.05
    PROFIT_RATE_WARNING: float = 0.10
    
    # ========== 日志配置 ==========
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "wberp.log"
    API_LOG_FILE: str = "wb_api.log"
    LOG_MAX_SIZE: int = 10
    LOG_BACKUP_COUNT: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
