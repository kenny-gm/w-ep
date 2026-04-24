"""
产品管理路由
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.models import Product, Shop, SyncLog
from app.routers.auth import get_current_user, get_current_admin
from app.services.sync import SyncService

router = APIRouter(prefix="/products", tags=["产品管理"])


# ========== 请求/响应模型 ==========

class ProductCreate(BaseModel):
    nm_id: str
    sku: str
    name: str
    custom_name: Optional[str] = None
    owner: Optional[str] = None
    weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None


class ProductUpdate(BaseModel):
    custom_name: Optional[str] = None
    owner: Optional[str] = None
    weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None


class ProductResponse(BaseModel):
    id: int
    nm_id: str
    sku: str
    shop_id: int
    name: str
    custom_name: Optional[str]
    owner: Optional[str]
    weight: Optional[float]
    length: Optional[float]
    width: Optional[float]
    height: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ========== 路由 ==========

@router.get("/", response_model=List[ProductResponse])
def list_products(
    shop_id: Optional[int] = None,
    owner: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取产品列表"""
    query = db.query(Product)
    
    if shop_id:
        query = query.filter(Product.shop_id == shop_id)
    
    if owner:
        query = query.filter(Product.owner == owner)
    
    if search:
        query = query.filter(
            Product.name.contains(search) |
            Product.custom_name.contains(search) |
            Product.sku.contains(search)
        )
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}/", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取产品详情"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product


@router.put("/{product_id}/", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新产品（自定义字段）"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 更新可编辑字段
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.post("/{product_id}/assign-owner/")
def assign_owner(
    product_id: int,
    owner: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """分配负责人"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    product.owner = owner
    db.commit()
    
    return {"message": f"产品 {product.nm_id} 分配给 {owner}"}


@router.post("/sync/{shop_id}/")
def sync_products_from_wildberries(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """从 WB 同步产品（只新增不覆盖）"""
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    
    sync_service = SyncService(db, shop)
    result = sync_service.sync_products()
    
    if result["success"]:
        return {
            "success": True,
            "message": f"成功同步 {result['count']} 个产品"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"同步失败: {result.get('error')}"
        )


@router.get("/owners/list/")
def list_owners(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取所有负责人列表"""
    owners = db.query(Product.owner).filter(Product.owner != None).distinct().all()
    return [o[0] for o in owners if o[0]]


@router.get("/{product_id}/ads/")
def get_product_ads(
    product_id: int,
    date_from: str = None,
    date_to: str = None,
    ad_type: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取产品广告数据"""
    from datetime import datetime, timedelta
    from app.services.wb_api import WBAPIClient
    
    # 获取产品信息
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 获取店铺信息
    shop = db.query(Shop).filter(Shop.id == product.shop_id).first()
    if not shop or not shop.api_token:
        raise HTTPException(status_code=400, detail="店铺没有API Token")
    
    # 设置默认日期
    if not date_to:
        date_to = datetime.now().strftime("%Y-%m-%d")
    if not date_from:
        date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # 创建API客户端
    client = WBAPIClient(shop.api_token)
    
    # 获取广告列表
    adverts = client.get_adverts()
    
    # 筛选该产品的广告
    product_ads = []
    product_ad_ids = []  # 该产品的广告ID列表
    nm_id = str(product.nm_id)
    for ad in adverts:
        nm_settings = ad.get("nm_settings", [])
        for nm in nm_settings:
            if str(nm.get("nm_id")) == nm_id:
                ad_data = {
                    "id": ad.get("id"),
                    "name": ad.get("settings", {}).get("name", ""),
                    "status": ad.get("status"),
                    "type": ad.get("settings", {}).get("payment_type", ""),
                    "bid_type": ad.get("bid_type"),
                }
                if ad_data not in product_ads:
                    product_ads.append(ad_data)
                    product_ad_ids.append(ad.get("id"))
    
    # 获取广告统计
    daily_data = []
    summary = {
        "impressions": 0,
        "clicks": 0,
        "ctr": 0,
        "spend": 0,
        "sales": 0,
        "roas": 0,
        "acos": 0
    }
    
    # 使用v3/fullstats API获取广告统计
    if product_ad_ids:
        try:
            stats = client.get_ad_stats(ids=product_ad_ids, date_from=date_from, date_to=date_to)
            
            # 解析统计数据
            for stat in stats:
                advert_id = stat.get("advertId")
                days = stat.get("days", [])
                
                for day in days:
                    date = day.get("date", "")[:10]  # 提取日期
                    day_views = day.get("views", 0)
                    day_clicks = day.get("clicks", 0)
                    day_spend = day.get("sum", 0)
                    
                    # 汇总
                    summary["impressions"] += day_views
                    summary["clicks"] += day_clicks
                    summary["spend"] += day_spend
                    
                    # 查找该天的产品数据
                    apps = day.get("apps", [])
                    for app in apps:
                        nms = app.get("nms", [])
                        for nm in nms:
                            if str(nm.get("nmId")) == nm_id:
                                nm_views = nm.get("views", 0)
                                nm_clicks = nm.get("clicks", 0)
                                nm_spend = nm.get("sum", 0)
                                nm_orders = nm.get("orders", 0)
                                nm_sales = nm.get("sum_price", 0)
                                
                                # 添加到每日数据
                                daily_data.append({
                                    "date": date,
                                    "impressions": nm_views,
                                    "clicks": nm_clicks,
                                    "spend": nm_spend,
                                    "orders": nm_orders,
                                    "sales": nm_sales
                                })
        except Exception as e:
            print(f"获取广告统计失败: {e}")
    
    # 计算CTR
    if summary["impressions"] > 0:
        summary["ctr"] = round(summary["clicks"] / summary["impressions"], 4)
    
    # 计算ROAS
    if summary["spend"] > 0:
        summary["roas"] = round(summary["sales"] / summary["spend"], 2)
    
    # 计算ACOS
    if summary["sales"] > 0:
        summary["acos"] = round(summary["spend"] / summary["sales"], 4)
    
    return {
        "summary": summary,
        "daily_data": daily_data,
        "adverts": product_ads
    }
