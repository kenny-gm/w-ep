"""
自定义异常模块 - 增强版
支持自动重试逻辑和详细信息
"""
from typing import Optional


class WBERPException(Exception):
    """WB ERP 基础异常"""
    def __init__(self, message: str = "系统错误"):
        self.message = message
        super().__init__(self.message)


# ========================================
# API 相关异常
# ========================================

class WBAPIException(WBERPException):
    """WB API 调用异常"""
    def __init__(
        self, 
        message: str = "API 调用失败", 
        status_code: Optional[int] = None,
        endpoint: Optional[str] = None,
        retry_count: int = 0
    ):
        self.status_code = status_code
        self.endpoint = endpoint
        self.retry_count = retry_count
        
        # 构建详细消息
        if endpoint:
            message = f"{message} (接口: {endpoint})"
        if retry_count > 0:
            message = f"{message} [已重试 {retry_count} 次]"
        
        super().__init__(message)


class WBAPIRateLimitException(WBAPIException):
    """API 限流异常 - 支持自动重试"""
    
    # 是否可自动重试
    retryable = True
    
    def __init__(
        self, 
        retry_after: int = 60, 
        endpoint: Optional[str] = None,
        retry_count: int = 0
    ):
        self.retry_after = retry_after
        
        message = f"API 限流，请在 {retry_after} 秒后重试"
        super().__init__(message, status_code=429, endpoint=endpoint, retry_count=retry_count)
    
    def should_retry(self, max_retries: int = 3) -> bool:
        """判断是否应该重试"""
        return self.retry_count < max_retries
    
    def get_wait_time(self) -> int:
        """获取建议等待时间"""
        # 指数退避：每次重试等待时间翻倍
        return self.retry_after * (2 ** self.retry_count)


class WBAuthException(WBAPIException):
    """认证异常（Token 过期/无效）"""
    
    retryable = False
    
    def __init__(self, token_expired: bool = False):
        self.token_expired = token_expired
        message = "API Token 已过期，请更新" if token_expired else "API Token 无效，请检查"
        super().__init__(message, status_code=401)


class WBAPIConnectionException(WBAPIException):
    """网络连接异常"""
    
    retryable = True
    
    def __init__(self, endpoint: Optional[str] = None, retry_count: int = 0):
        message = "无法连接到 WB API，请检查网络"
        super().__init__(message, endpoint=endpoint, retry_count=retry_count)


class WBAPIErrorException(WBAPIException):
    """API 返回错误（400/422 等）"""
    
    retryable = False
    
    def __init__(
        self, 
        status_code: int, 
        error_detail: str,
        endpoint: Optional[str] = None
    ):
        self.error_detail = error_detail
        message = f"API 错误 [{status_code}]: {error_detail}"
        super().__init__(message, status_code=status_code, endpoint=endpoint)


# ========================================
# 同步相关异常
# ========================================

class WBDataSyncException(WBERPException):
    """数据同步异常"""
    def __init__(self, sync_type: str, error_detail: str, records_processed: int = 0):
        self.sync_type = sync_type
        self.error_detail = error_detail
        self.records_processed = records_processed
        
        message = f"[{sync_type}] 同步失败: {error_detail}"
        if records_processed > 0:
            message += f" (已处理 {records_processed} 条)"
        
        super().__init__(message)


class SyncInProgressException(WBERPException):
    """同步进行中异常"""
    def __init__(self, sync_type: str, started_at: Optional[str] = None):
        self.sync_type = sync_type
        self.started_at = started_at
        
        message = f"[{sync_type}] 同步正在进行中"
        if started_at:
            message += f"（开始于 {started_at}）"
        
        super().__init__(message)


# ========================================
# 业务相关异常
# ========================================

class ProductNotFoundException(WBERPException):
    """产品不存在"""
    def __init__(self, product_id: Optional[str] = None, nm_id: Optional[str] = None):
        self.product_id = product_id
        self.nm_id = nm_id
        
        if nm_id:
            message = f"产品 nm_id={nm_id} 不存在"
        elif product_id:
            message = f"产品 ID={product_id} 不存在"
        else:
            message = "产品不存在"
        
        super().__init__(message)


class OrderNotFoundException(WBERPException):
    """订单不存在"""
    def __init__(self, order_id: Optional[str] = None):
        msg = f"订单 {order_id} 不存在" if order_id else "订单不存在"
        super().__init__(msg)


class InsufficientStockException(WBERPException):
    """库存不足"""
    def __init__(self, product_id: str, required: int, available: int):
        self.product_id = product_id
        self.required = required
        self.available = available
        
        super().__init__(f"产品 {product_id} 库存不足，需要 {required}，可用 {available}")


# ========================================
# 权限相关异常
# ========================================

class PermissionDeniedException(WBERPException):
    """权限不足"""
    def __init__(self, resource: Optional[str] = None, action: Optional[str] = None):
        self.resource = resource
        self.action = action
        
        message = "权限不足"
        if resource and action:
            message = f"无权限 {action} {resource}"
        
        super().__init__(message)


class TokenExpiredException(WBERPException):
    """登录 Token 过期"""
    def __init__(self):
        super().__init__("登录已过期，请重新登录")


# ========================================
# 配置相关异常
# ========================================

class ConfigurationException(WBERPException):
    """配置错误"""
    def __init__(self, config_name: str, expected_type: Optional[str] = None):
        self.config_name = config_name
        self.expected_type = expected_type
        
        message = f"配置项 '{config_name}' 未设置或格式错误"
        if expected_type:
            message += f"，期望类型: {expected_type}"
        
        super().__init__(message)
