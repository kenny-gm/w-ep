"""
日志配置模块
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logger(
    name: str = "wberp",
    log_file: str = None,
    level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    配置并返回日志记录器
    
    Args:
        name: 日志器名称
        log_file: 日志文件路径（相对于 logs 目录）
        level: 日志级别
        max_bytes: 单个日志文件最大大小
        backup_count: 保留的备份文件数量
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_file:
        file_path = LOG_DIR / log_file
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_wberp_logger() -> logging.Logger:
    """获取主应用日志记录器"""
    from app.config import settings
    return setup_logger(
        name="wberp",
        log_file="wberp.log",
        level=settings.LOG_LEVEL if hasattr(settings, 'LOG_LEVEL') else "INFO",
        max_bytes=getattr(settings, 'LOG_MAX_SIZE', 10) * 1024 * 1024,
        backup_count=getattr(settings, 'LOG_BACKUP_COUNT', 5)
    )


def get_api_logger() -> logging.Logger:
    """获取 WB API 调用日志记录器"""
    from app.config import settings
    return setup_logger(
        name="wb_api",
        log_file="wb_api.log",
        level="DEBUG",  # API 调用记录详细日志
        max_bytes=getattr(settings, 'LOG_MAX_SIZE', 10) * 1024 * 1024,
        backup_count=getattr(settings, 'LOG_BACKUP_COUNT', 5)
    )


def get_sync_logger() -> logging.Logger:
    """获取数据同步日志记录器"""
    from app.config import settings
    return setup_logger(
        name="sync",
        log_file="sync.log",
        level="INFO",
        max_bytes=getattr(settings, 'LOG_MAX_SIZE', 10) * 1024 * 1024,
        backup_count=getattr(settings, 'LOG_BACKUP_COUNT', 5)
    )
