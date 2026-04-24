"""
订单管理路由
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.models import Order, OrderItem
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/orders", tags=["订单管理"])


@router.get("/")
def list_orders(
    skip: int = 0,
    limit: int = 20,
    shop_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取订单列表"""
    query = db.query(Order)
    
    if shop_id:
        query = query.filter(Order.shop_id == shop_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    if start_date:
        query = query.filter(Order.order_date >= datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d"))
    
    if end_date:
        query = query.filter(Order.order_date < (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"))
    
    total = query.count()
    orders = query.order_by(Order.order_date.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                "id": o.id,
                "order_id": o.order_id,
                "shop_id": o.shop_id,
                "status": o.status,
                "total_amount": o.total_amount,
                "commission": o.commission,
                "logistics_fee": o.logistics_fee,
                "product_cost": o.product_cost,
                "ad_cost": o.ad_cost,
                "other_cost": o.other_cost,
                "profit": o.profit,
                "profit_rate": o.profit_rate,
                "order_date": o.order_date,
                "created_at": o.created_at
            }
            for o in orders
        ],
        "total": total
    }


@router.get("/{order_id}/")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"error": "订单不存在"}
    
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    
    return {
        **order.__dict__,
        "items": [
            {
                "id": i.id,
                "nm_id": i.nm_id,
                "sku": i.sku,
                "quantity": i.quantity,
                "price": i.price,
                "total_price": i.total_price,
                "product_cost": i.product_cost
            }
            for i in items
        ]
    }


@router.get("/stats/summary/")
def order_stats(
    shop_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """订单统计"""
    query = db.query(Order)
    
    if shop_id:
        query = query.filter(Order.shop_id == shop_id)
    
    if start_date:
        query = query.filter(Order.order_date >= datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d"))
    
    if end_date:
        query = query.filter(Order.order_date < (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"))
    
    orders = query.all()
    
    return {
        "total_orders": len(orders),
        "total_amount": sum(o.total_amount for o in orders),
        "total_profit": sum(o.profit for o in orders),
        "total_commission": sum(o.commission for o in orders),
        "total_logistics": sum(o.logistics_fee for o in orders),
        "avg_profit_rate": sum(o.profit_rate for o in orders) / len(orders) if orders else 0
    }
