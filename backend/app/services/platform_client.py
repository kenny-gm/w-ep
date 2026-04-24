"""
平台客户端抽象层
支持多平台：Wildberries、Yandex 等
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BasePlatformClient(ABC):
    """平台客户端基类"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
    
    @abstractmethod
    def get_products(self, limit: int = 100, offset: int = 0, locale: str = "ru") -> List[Dict[str, Any]]:
        """获取商品列表"""
        pass
    
    @abstractmethod
    def get_products_from_statistics(self) -> List[Dict[str, Any]]:
        """从统计API获取商品列表"""
        pass
    
    @abstractmethod
    def get_product_analytics(self, nm_id: str, days: int = 7) -> Dict[str, Any]:
        """获取商品分析数据"""
        pass
    
    @abstractmethod
    def get_advertising_campaigns(self) -> List[Dict[str, Any]]:
        """获取广告活动列表"""
        pass
    
    @abstractmethod
    def get_advertising_stats(self, campaign_id: int, days: int = 7) -> Dict[str, Any]:
        """获取广告统计数据"""
        pass
    
    @abstractmethod
    def get_new_orders(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """获取新订单"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """测试连接"""
        pass


# 平台客户端注册表
PLATFORM_CLIENTS = {}


def register_platform_client(platform: str, client_class: type):
    """注册平台客户端"""
    PLATFORM_CLIENTS[platform] = client_class


def get_platform_client(platform: str, api_token: str) -> BasePlatformClient:
    """获取指定平台的客户端"""
    if platform not in PLATFORM_CLIENTS:
        raise ValueError(f"不支持的平台: {platform}，已注册的平台: {list(PLATFORM_CLIENTS.keys())}")
    return PLATFORM_CLIENTS[platform](api_token)
