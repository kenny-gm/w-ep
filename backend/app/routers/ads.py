"""
广告分析路由
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import AdRecord, Product, Shop, User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/ads", tags=["广告分析"])


@router.get("/")
def list_ads(
    skip: int = 0,
    limit: int = 20,
    shop_id: Optional[int] = None,
    ad_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取广告数据列表"""
    from app.models.models import ProductPermission
    
    allowed_product_ids = None
    if current_user.role != "admin":
        if current_user.allowed_owners:
            products = db.query(Product.id).filter(Product.owner.in_(current_user.allowed_owners)).all()
            allowed_product_ids = [p[0] for p in products]
        else:
            perms = db.query(ProductPermission.product_id).filter(ProductPermission.user_id == current_user.id).all()
            allowed_product_ids = [p[0] for p in perms]
        if not allowed_product_ids:
            return {"total": 0, "items": []}
    
    query = db.query(AdRecord)

    if allowed_product_ids is not None:
        query = query.filter(AdRecord.product_id.in_(allowed_product_ids))

    if shop_id:
        query = query.filter(AdRecord.shop_id == shop_id)

    if ad_type:
        query = query.filter(AdRecord.ad_type == ad_type)

    if start_date:
        query = query.filter(AdRecord.record_date >= datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d"))

    if end_date:
        query = query.filter(AdRecord.record_date < end_date)

    total = query.count()
    records = query.order_by(AdRecord.record_date.desc()).offset(skip).limit(limit).all()
    
    items = []
    for r in records:
        product = db.query(Product).filter(Product.id == r.product_id).first()
        items.append({
            "id": r.id,
            "shop_id": r.shop_id,
            "product_id": r.product_id,
            "ad_type": r.ad_type,
            "record_date": r.record_date,
            "views": r.impressions,
            "clicks": r.visitors,
            "ctr": r.ctr,
            "cost": r.cost,  # 原始数据，已经是卢布
            "sales": r.sales,
            "orders": r.order_count,
            "cpc": r.cpc,
            "cpm": r.cpm,
            "acos": r.acos,
            "roas": r.roas,
            "product": {"id": product.id, "nm_id": product.nm_id, "name": product.name, "custom_name": product.custom_name} if product else None,
            "currency": "RUB"
        })
    
    return {"items": items, "total": total, "currency": "RUB"}


@router.get("/summary/")
def ad_summary(
    shop_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """广告数据汇总"""
    from app.models.models import ProductPermission
    
    allowed_product_ids = None
    if current_user.role != "admin":
        if current_user.allowed_owners:
            products = db.query(Product.id).filter(Product.owner.in_(current_user.allowed_owners)).all()
            allowed_product_ids = [p[0] for p in products]
        else:
            perms = db.query(ProductPermission.product_id).filter(ProductPermission.user_id == current_user.id).all()
            allowed_product_ids = [p[0] for p in perms]
        if not allowed_product_ids:
            return {"total_impressions": 0, "total_clicks": 0, "total_cost": 0, "total_sales": 0, "total_orders": 0, "avg_ctr": 0, "avg_cpc": 0, "avg_cpm": 0, "avg_acos": 0}
    
    query = db.query(AdRecord)

    if allowed_product_ids is not None:
        query = query.filter(AdRecord.product_id.in_(allowed_product_ids))

    if shop_id:
        query = query.filter(AdRecord.shop_id == shop_id)

    if start_date:
        query = query.filter(AdRecord.record_date >= datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d"))

    if end_date:
        query = query.filter(AdRecord.record_date < end_date)

    # 广告指标使用 advertising 类型
    ad_query = query.filter(AdRecord.ad_type == "advertising")
    ad_records = ad_query.all()

    total_impressions = sum(r.impressions or 0 for r in ad_records)
    total_clicks = sum(r.visitors or 0 for r in ad_records)
    total_cost = sum(r.cost or 0 for r in ad_records)

    # 销售指标使用 product_analytics 类型（与销售看板一致）
    sales_query = query.filter(AdRecord.ad_type == "product_analytics")
    sales_records = sales_query.all()
    
    total_sales = sum(r.sales or 0 for r in sales_records)
    total_orders = sum(r.order_count or 0 for r in sales_records)
    
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_cpc = (total_cost / total_clicks) if total_clicks > 0 else 0
    avg_cpm = (total_cost / total_impressions * 1000) if total_impressions > 0 else 0
    avg_acos = (total_cost / total_sales * 100) if total_sales > 0 else 0
    
    return {
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_cost": round(total_cost, 2),
        "total_sales": round(total_sales, 2),
        "total_orders": total_orders,
        "avg_ctr": round(avg_ctr, 2),
        "avg_cpc": round(avg_cpc, 2),
        "avg_cpm": round(avg_cpm, 2),
        "avg_acos": round(avg_acos, 2),
        "currency": "RUB"
    }


@router.get("/by-product/")
def ads_by_product(
    shop_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """按产品汇总广告数据"""
    from app.models.models import ProductPermission
    
    allowed_product_ids = None
    if current_user.role != "admin":
        if current_user.allowed_owners:
            products = db.query(Product.id).filter(Product.owner.in_(current_user.allowed_owners)).all()
            allowed_product_ids = [p[0] for p in products]
        else:
            perms = db.query(ProductPermission.product_id).filter(ProductPermission.user_id == current_user.id).all()
            allowed_product_ids = [p[0] for p in perms]
        if not allowed_product_ids:
            return []
    
    query = db.query(
        AdRecord.product_id,
        func.sum(AdRecord.impressions).label("impressions"),
        func.sum(AdRecord.visitors).label("clicks"),
        func.sum(AdRecord.cost).label("cost"),
        func.sum(AdRecord.sales).label("sales"),
        func.sum(AdRecord.order_count).label("orders"),
        func.avg(AdRecord.ctr).label("avg_ctr"),
        func.avg(AdRecord.cpc).label("avg_cpc"),
        func.avg(AdRecord.cpm).label("avg_cpm"),
        func.avg(AdRecord.acos).label("avg_acos"),
        func.avg(AdRecord.roas).label("avg_roas")
    )

    if allowed_product_ids is not None:
        query = query.filter(AdRecord.product_id.in_(allowed_product_ids))

    if shop_id:
        query = query.filter(AdRecord.shop_id == shop_id)

    if start_date:
        query = query.filter(AdRecord.record_date >= datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d"))

    if end_date:
        query = query.filter(AdRecord.record_date < end_date)

    results = query.group_by(AdRecord.product_id).all()
    
    data = []
    for r in results:
        product = db.query(Product).filter(Product.id == r.product_id).first()
        data.append({
            "product_id": r.product_id,
            "product_name": product.name if product else None,
            "impressions": int(r.impressions or 0),
            "clicks": int(r.visitors or 0),
            "cost": round(r.cost or 0, 2),  # 直接返回卢布
            "sales": round(r.sales or 0, 2),
            "orders": int(r.order_count or 0),
            "avg_ctr": round(r.avg_ctr or 0, 2),
            "avg_cpc": round(r.avg_cpc or 0, 2),
            "avg_cpm": round(r.avg_cpm or 0, 2),
            "avg_acos": round(r.avg_acos or 0, 2),
            "avg_roas": round(r.avg_roas or 0, 2),
            "currency": "RUB"
        })

    return data


@router.get("/unified-bidding/summary/")
def unified_bidding_summary(
    shop_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """“统一出价”广告汇总 (Kenny 16:08 定义: payment_type=cpm + placements=search+rec)

    返回:
    - 总指标 (impressions / clicks / cost / advert 数量)
    - 按 advert_id 聚合的广告列表 (按 cost 倒序)
    """
    from app.models.models import ProductPermission
    from app.routers.dashboard import get_ad_form, get_shop_exchange_rates, convert_ad_cost

    allowed_product_ids = None
    if current_user.role != "admin":
        if current_user.allowed_owners:
            products = db.query(Product.id).filter(Product.owner.in_(current_user.allowed_owners)).all()
            allowed_product_ids = [p[0] for p in products]
        else:
            perms = db.query(ProductPermission.product_id).filter(ProductPermission.user_id == current_user.id).all()
            allowed_product_ids = [p[0] for p in perms]
        if not allowed_product_ids:
            return {
                "total_impressions": 0, "total_clicks": 0, "total_cost": 0,
                "total_sales": 0, "total_orders": 0, "total_advert_count": 0,
                "adverts": [], "currency": "RUB", "definition": "payment_type=cpm + placements=search+rec",
            }

    query = db.query(AdRecord).filter(AdRecord.ad_type == "advertising")

    if allowed_product_ids is not None:
        query = query.filter(AdRecord.product_id.in_(allowed_product_ids))

    if shop_id:
        query = query.filter(AdRecord.shop_id == shop_id)

    if start_date:
        query = query.filter(
            AdRecord.record_date >= datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        )

    if end_date:
        query = query.filter(AdRecord.record_date < end_date)

    # 过滤统一出价 (cpm + search+rec)
    all_records = query.all()
    records = [r for r in all_records if get_ad_form(r) == "统一出价"]

    shop_rates = get_shop_exchange_rates(db)

    total_impressions = sum(r.impressions or 0 for r in records)
    total_clicks = sum(r.visitors or 0 for r in records)
    total_cost = sum(convert_ad_cost(r, shop_rates) for r in records)
    total_sales = sum(r.sales or 0 for r in records)
    total_orders = sum(r.order_count or 0 for r in records)

    # 按 advert_id 聚合
    advert_summary: dict = {}
    for r in records:
        aid = r.advert_id
        if aid not in advert_summary:
            advert_summary[aid] = {
                "advert_id": aid,
                "impressions": 0,
                "clicks": 0,
                "cost": 0.0,
                "sales": 0.0,
                "orders": 0,
                "first_date": r.record_date,
                "last_date": r.record_date,
                "record_count": 0,
                "shop_ids": set(),
            }
        advert_summary[aid]["impressions"] += r.impressions or 0
        advert_summary[aid]["clicks"] += r.visitors or 0
        advert_summary[aid]["cost"] += convert_ad_cost(r, shop_rates)
        advert_summary[aid]["sales"] += r.sales or 0
        advert_summary[aid]["orders"] += r.order_count or 0
        advert_summary[aid]["record_count"] += 1
        advert_summary[aid]["shop_ids"].add(r.shop_id)
        if r.record_date < advert_summary[aid]["first_date"]:
            advert_summary[aid]["first_date"] = r.record_date
        if r.record_date > advert_summary[aid]["last_date"]:
            advert_summary[aid]["last_date"] = r.record_date

    advert_list = []
    for ad in sorted(advert_summary.values(), key=lambda x: x["cost"], reverse=True):
        ad["cost"] = round(ad["cost"], 2)
        ad["sales"] = round(ad["sales"], 2)
        ad["shop_ids"] = sorted(list(ad["shop_ids"]))
        ad["first_date"] = ad["first_date"].isoformat() if ad["first_date"] else None
        ad["last_date"] = ad["last_date"].isoformat() if ad["last_date"] else None
        advert_list.append(ad)

    return {
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_cost": round(total_cost, 2),
        "total_sales": round(total_sales, 2),
        "total_orders": total_orders,
        "total_advert_count": len(advert_summary),
        "adverts": advert_list,
        "currency": "RUB",
        "definition": "payment_type=cpm + placements=search+rec",
    }
