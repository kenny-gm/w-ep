"""
时区工具函数
"""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from app.config import settings


def get_shanghai_now() -> datetime:
    """获取上海当前时间"""
    return datetime.now(ZoneInfo("Asia/Shanghai"))


def get_shanghai_date() -> datetime:
    """获取上海当前日期（无时区）"""
    return datetime.now(ZoneInfo("Asia/Shanghai")).replace(tzinfo=None)


def to_shanghai(dt: datetime) -> datetime:
    """将任意时区时间转换为上海时间"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # 无时区的时间假设为UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ZoneInfo("Asia/Shanghai"))


def format_shanghai_time(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化上海时间"""
    if dt is None:
        return "-"
    sh_dt = to_shanghai(dt)
    return sh_dt.strftime(fmt)


def get_shanghai_str_date() -> str:
    """获取上海当前日期字符串"""
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
