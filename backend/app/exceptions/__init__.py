"""
异常模块入口
"""
from app.exceptions.wb_exceptions import (
    # 基础异常
    WBERPException,
    
    # API 异常
    WBAPIException,
    WBAPIRateLimitException,
    WBAuthException,
    WBAPIConnectionException,
    WBAPIErrorException,
    
    # 同步异常
    WBDataSyncException,
    SyncInProgressException,
    
    # 业务异常
    ProductNotFoundException,
    OrderNotFoundException,
    InsufficientStockException,
    
    # 权限异常
    PermissionDeniedException,
    TokenExpiredException,
    
    # 配置异常
    ConfigurationException,
)

__all__ = [
    "WBERPException",
    "WBAPIException",
    "WBAPIRateLimitException",
    "WBAuthException",
    "WBAPIConnectionException",
    "WBAPIErrorException",
    "WBDataSyncException",
    "SyncInProgressException",
    "ProductNotFoundException",
    "OrderNotFoundException",
    "InsufficientStockException",
    "PermissionDeniedException",
    "TokenExpiredException",
    "ConfigurationException",
]
