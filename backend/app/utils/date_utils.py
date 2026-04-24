"""
日期工具函数 - 统一使用 YYYY-MM-DD 字符串格式
"""
from datetime import datetime, timedelta, date
from typing import Union, Tuple


def to_date_str(d: Union[str, datetime, date, None]) -> str:
    """
    将各种日期类型转换为 YYYY-MM-DD 字符串
    
    Args:
        d: 日期对象，可以是字符串、datetime、date 或 None
        
    Returns:
        YYYY-MM-DD 格式的字符串，如果输入为 None 返回空字符串
    """
    if d is None:
        return ""
    
    if isinstance(d, str):
        # 如果已经是字符串，截取前10位
        return d[:10] if len(d) >= 10 else d
    
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d")
    
    if isinstance(d, date):
        return d.strftime("%Y-%m-%d")
    
    return str(d)[:10]


def get_today_str() -> str:
    """
    获取今日日期字符串
    
    Returns:
        YYYY-MM-DD 格式的今日日期
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_yesterday_str() -> str:
    """
    获取昨日日期字符串
    
    Returns:
        YYYY-MM-DD 格式的昨日日期
    """
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def get_date_range_str(days: int = 7) -> Tuple[str, str]:
    """
    获取日期范围字符串
    
    Args:
        days: 天数，默认7天
        
    Returns:
        (start_date, end_date) 元组，都是 YYYY-MM-DD 格式
    """
    end = datetime.now()
    start = end - timedelta(days=days - 1)
    return to_date_str(start), to_date_str(end)


def date_add_days(d: str, days: int) -> str:
    """
    日期加减天数
    
    Args:
        d: YYYY-MM-DD 格式的日期字符串
        days: 要加的天数（负数为减）
        
    Returns:
        新的 YYYY-MM-DD 格式日期字符串
    """
    dt = datetime.strptime(d, "%Y-%m-%d")
    new_dt = dt + timedelta(days=days)
    return to_date_str(new_dt)
