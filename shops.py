"""
店铺管理路由
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_serializer

from app.database import get_db
from app.models.models import Shop, SyncLog
from app.routers.auth import get_current_user, get_current_admin
from app.services.sync import SyncService
from app.utils.timezone import format_shanghai_time

router = APIRouter(prefix="/shops", tags=["店铺管理"])


# ========== 请求/响应模型 ==========

class ShopCreate(BaseModel):
    name: str
    api_token: Optional[str] = None  # 允许为空，后续再配置
    currency: str = "RUB"
    sync_interval_hours: int = 24


class ShopUpdate(BaseModel):
    name: Optional[str] = None
    api_token: Optional[str] = None
    currency: Optional[str] = None
    sync_enabled: Optional[bool] = None
    sync_interval_hours: Optional[int] = None


class ShopResponse(BaseModel):
    id: int
    name: str
    currency: str
    sync_enabled: bool
    sync_interval_hours: int
    last_sync_at: Optional[str] = None  # 格式化的时间字符串
    is_active: bool
    created_at: str  # 格式化的时间字符串
    
    class Config:
        from_attributes = True


# ========== 路由 ==========

@router.get("/")
def list_shops(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取店铺列表"""
    shops = db.query(Shop).filter(Shop.is_active == True).all()
    
    # 转换时间为格式化字符串
    result = []
    for shop in shops:
        result.append({
            "id": shop.id,
            "name": shop.name,
            "currency": shop.currency,
            "api_token": shop.api_token[:20] + "..." if shop.api_token and len(shop.api_token) > 20 else shop.api_token,
            "has_token": bool(shop.api_token),
            "sync_enabled": shop.sync_enabled,
            "sync_interval_hours": shop.sync_interval_hours,
            "last_sync_at": shop.last_sync_at.strftime("%Y-%m-%d %H:%M:%S") if shop.last_sync_at else None,
            "is_active": shop.is_active,
            "created_at": shop.created_at.strftime("%Y-%m-%d %H:%M:%S") if shop.created_at else None
        })
    
    return result


@router.get("/{shop_id}/")
def get_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单个店铺详情"""
    shop = db.query(Shop).filter(Shop.id == shop_id, Shop.is_active == True).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    return {
        "id": shop.id,
        "name": shop.name,
        "currency": shop.currency,
        "api_token": shop.api_token[:20] + "..." if shop.api_token and len(shop.api_token) > 20 else shop.api_token,  # 只显示前20位
        "has_token": bool(shop.api_token),  # 是否有Token
        "sync_enabled": shop.sync_enabled,
        "sync_interval_hours": shop.sync_interval_hours,
        "last_sync_at": shop.last_sync_at.strftime("%Y-%m-%d %H:%M:%S") if shop.last_sync_at else None,
        "is_active": shop.is_active,
        "created_at": shop.created_at.strftime("%Y-%m-%d %H:%M:%S") if shop.created_at else None
    }


@router.post("/")
def create_shop(
    data: ShopCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """创建店铺"""
    shop = Shop(
        name=data.name,
        api_token=data.api_token,
        currency=data.currency,
        sync_interval_hours=data.sync_interval_hours
    )
    
    db.add(shop)
    db.commit()
    db.refresh(shop)
    
    # 返回格式化后的数据
    return {
        "id": shop.id,
        "name": shop.name,
        "currency": shop.currency,
        "api_token": shop.api_token[:20] + "..." if shop.api_token and len(shop.api_token) > 20 else shop.api_token,
        "has_token": bool(shop.api_token),
        "sync_enabled": shop.sync_enabled,
        "sync_interval_hours": shop.sync_interval_hours,
        "last_sync_at": shop.last_sync_at.strftime("%Y-%m-%d %H:%M:%S") if shop.last_sync_at else None,
        "is_active": shop.is_active,
        "created_at": shop.created_at.strftime("%Y-%m-%d %H:%M:%S") if shop.created_at else None
    }


@router.put("/{shop_id}/")
def update_shop(
    shop_id: int,
    data: ShopUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """更新店铺"""
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shop, key, value)
    
    db.commit()
    db.refresh(shop)
    
    # 返回格式化后的数据
    return {
        "id": shop.id,
        "name": shop.name,
        "currency": shop.currency,
        "api_token": shop.api_token[:20] + "..." if shop.api_token and len(shop.api_token) > 20 else shop.api_token,
        "has_token": bool(shop.api_token),
        "sync_enabled": shop.sync_enabled,
        "sync_interval_hours": shop.sync_interval_hours,
        "last_sync_at": shop.last_sync_at.strftime("%Y-%m-%d %H:%M:%S") if shop.last_sync_at else None,
        "is_active": shop.is_active,
        "created_at": shop.created_at.strftime("%Y-%m-%d %H:%M:%S") if shop.created_at else None
    }


@router.delete("/{shop_id}/")
def delete_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """删除店铺（软删除）"""
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    shop.is_active = False
    db.commit()
    
    return {"message": "店铺已删除"}


@router.post("/{shop_id}/test-connection/")
def test_connection(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """测试 API 连接"""
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    from app.services.wb_api import WBAPIClient
    client = WBAPIClient(shop.api_token)
    
    # 测试连接
    if client.ping():
        return {"success": True, "message": "连接成功"}
    else:
        return {"success": False, "message": "连接失败，请检查 API Token"}


@router.post("/{shop_id}/sync/")
def sync_shop_data(
    shop_id: int,
    sync_type: str = "all",  # products/orders/inventory/ads/all
    history: bool = False,   # 是否同步历史数据
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """手动同步数据
    
    Args:
        shop_id: 店铺ID
        sync_type: 同步类型 (products/orders/inventory/ads/all)
        history: 是否同步历史数据（新店铺自动检测）
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"========== 开始同步店铺 {shop_id} ==========")
    
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        logger.error(f"店铺 {shop_id} 不存在")
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    logger.info(f"店铺信息: {shop.name}, API Token: {shop.api_token[:10]}...")
    
    sync_service = SyncService(db, shop)
    
    # 自动检测新店铺
    is_new = shop.last_sync_at is None
    if is_new:
        logger.info("检测到新店铺，将同步历史数据")
        history = True  # 新店铺自动同步历史数据
    
    logger.info(f"同步类型: {sync_type}, 历史数据: {history}")
    
    results = {}
    
    try:
        if sync_type == "products":
            logger.info("开始同步产品数据...")
            results["products"] = sync_service.sync_products(overwrite=True)
            logger.info(f"产品同步完成: {results['products']}")
        elif sync_type == "orders":
            logger.info("开始同步订单数据...")
            results["orders"] = sync_service.sync_orders()
            logger.info(f"订单同步完成: {results['orders']}")
        elif sync_type == "inventory":
            logger.info("开始同步库存数据...")
            results["inventory"] = sync_service.sync_inventory()
            logger.info(f"库存同步完成: {results['inventory']}")
        elif sync_type == "ads":
            logger.info("开始同步广告数据...")
            results["ads"] = sync_service.sync_ads(days=90 if history else None)
            logger.info(f"广告同步完成: {results['ads']}")
        elif sync_type == "all":
            logger.info("开始全量同步...")
            results = sync_service.sync_all(history=history)
            logger.info(f"全量同步完成: {results}")
    except Exception as e:
        logger.error(f"同步失败: {str(e)}", exc_info=True)
        return {
            "is_new_shop": is_new,
            "error": str(e),
            "results": results
        }
    
    logger.info(f"========== 同步店铺 {shop_id} 完成 ==========")
    
    return {
        "is_new_shop": is_new,
        "results": results
    }


@router.get("/{shop_id}/sync-logs/")
def get_sync_logs(
    shop_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取同步日志"""
    logs = db.query(SyncLog).filter(
        SyncLog.shop_id == shop_id
    ).order_by(SyncLog.started_at.desc()).limit(limit).all()
    
    return logs


@router.get("/{shop_id}/products/")
def get_shop_products(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取店铺的产品列表"""
    from app.models.models import Product
    
    # 验证店铺是否存在
    shop = db.query(Shop).filter(Shop.id == shop_id, Shop.is_active == True).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 获取该店铺的所有产品
    products = db.query(Product).filter(Product.shop_id == shop_id).all()
    
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "nm_id": p.nm_id,
            "sku": p.sku,
            "name": p.custom_name or p.name or p.sku,
            "shop_id": p.shop_id
        })
    
    return result


@router.get("/{shop_id}/traffic-source/")
def get_traffic_source(
    shop_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取流量来源分析"""
    from app.models.models import Product, Order, AdRecord
    from app.services.wb_api import WBAPIClient
    from datetime import timedelta
    
    # 验证店铺
    shop = db.query(Shop).filter(Shop.id == shop_id, Shop.is_active == True).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    # 默认时间范围
    if not date_to:
        date_to = datetime.now().strftime("%Y-%m-%d")
    if not date_from:
        date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # 尝试从API获取广告数据
    ad_clicks = 0
    ad_impressions = 0
    ad_spend = 0
    
    if shop.api_token:
        try:
            client = WBAPIClient(shop.api_token)
            adverts = client.get_adverts()
            
            # 尝试获取统计数据
            ad_ids = [ad.get("id") for ad in adverts if ad.get("id")]
            if ad_ids:
                try:
                    stats = client.get_ad_stats(ids=ad_ids, date_from=date_from, date_to=date_to)
                    for stat in stats:
                        for day in stat.get("days", []):
                            ad_impressions += day.get("views", 0)
                            ad_clicks += day.get("clicks", 0)
                            ad_spend += day.get("sum", 0)
                except Exception as e:
                    print(f"获取广告统计失败: {e}")
        except Exception as e:
            print(f"获取广告列表失败: {e}")
    
    # 从数据库获取订单数据估算自然流量
    try:
        orders = db.query(Order).filter(
            Order.shop_id == shop_id,
            Order.created_at >= datetime.strptime(date_from, "%Y-%m-%d"),
            Order.created_at <= datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
        ).all()
        total_orders = len(orders)
    except:
        total_orders = 0
    
    # 估算流量
    # 假设：每100次广告点击带来约1个订单，转化率1%
    # 自然流量订单 = 总订单 - 广告订单
    # 假设广告订单占比约30%
    ad_orders = int(ad_clicks * 0.01) if ad_clicks > 0 else int(total_orders * 0.3)
    natural_orders = max(0, total_orders - ad_orders)
    
    # 估算访客数（假设转化率）
    ad_visitors = ad_clicks  # 广告点击作为广告访客
    natural_visitors = natural_orders * 100  # 假设1%转化率
    total_visitors = ad_visitors + natural_visitors
    
    if total_visitors > 0:
        ad_ratio = round(ad_visitors / total_visitors * 100, 1)
        natural_ratio = round(natural_visitors / total_visitors * 100, 1)
        other_ratio = round(100 - ad_ratio - natural_ratio, 1)
    else:
        ad_ratio = 25.0
        natural_ratio = 73.0
        other_ratio = 2.0
    
    return {
        "date_from": date_from,
        "date_to": date_to,
        "total_visitors": total_visitors,
        "ad_visitors": ad_visitors,
        "natural_visitors": natural_visitors,
        "other_visitors": 0,
        "ad_ratio": ad_ratio,
        "natural_ratio": natural_ratio,
        "other_ratio": other_ratio,
        "ad_clicks": ad_clicks,
        "ad_impressions": ad_impressions,
        "ad_spend": ad_spend,
        "total_orders": total_orders,
        "ad_orders": ad_orders,
        "natural_orders": natural_orders
    }
