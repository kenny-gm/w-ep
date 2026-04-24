"""
库存管理路由
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.models import InventoryRecord, Product
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/inventory", tags=["库存管理"])


# ========== 请求/响应模型 ==========

class InboundRequest(BaseModel):
    product_id: int
    quantity: int
    product_cost: float
    logistics_cost: float = 0
    warehouse_type: str = "own"  # FBW/FBS/own
    note: Optional[str] = None


class InventoryRecordResponse(BaseModel):
    id: int
    product_id: int
    product: Optional[dict]
    quantity: int
    remaining_quantity: int
    product_cost: float
    logistics_cost: float
    warehouse_type: str
    inbound_at: datetime
    note: Optional[str]
    
    class Config:
        from_attributes = True


# ========== 路由 ==========

@router.get("/records/")
def list_records(
    skip: int = 0,
    limit: int = 20,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取入库记录列表"""
    query = db.query(InventoryRecord)
    
    if product_id:
        query = query.filter(InventoryRecord.product_id == product_id)
    
    total = query.count()
    records = query.order_by(InventoryRecord.inbound_at.desc()).offset(skip).limit(limit).all()
    
    # 关联产品信息
    items = []
    for r in records:
        product = db.query(Product).filter(Product.id == r.product_id).first()
        items.append({
            **r.__dict__,
            "product": {
                "id": product.id,
                "nm_id": product.nm_id,
                "name": product.name,
                "custom_name": product.custom_name
            } if product else None
        })
    
    return {"items": items, "total": total}


@router.post("/inbound/")
def create_inbound(
    data: InboundRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """手动入库"""
    # 检查产品
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    record = InventoryRecord(
        product_id=data.product_id,
        quantity=data.quantity,
        remaining_quantity=data.quantity,  # 初始剩余等于入库数量
        product_cost=data.product_cost,
        logistics_cost=data.logistics_cost,
        warehouse_type=data.warehouse_type,
        note=data.note
    )
    
    db.add(record)
    db.commit()
    
    return {"success": True, "message": f"入库成功，数量: {data.quantity}"}


@router.get("/product/{product_id}/")
def get_product_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取产品库存信息"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 获取入库记录
    records = db.query(InventoryRecord).filter(
        InventoryRecord.product_id == product_id,
        InventoryRecord.remaining_quantity > 0
    ).all()
    
    total_quantity = sum(r.remaining_quantity for r in records)
    total_cost = sum(r.remaining_quantity * r.product_cost for r in records)
    avg_cost = total_cost / total_quantity if total_quantity > 0 else 0
    
    return {
        "product_id": product_id,
        "total_quantity": total_quantity,
        "total_value": total_cost,
        "avg_cost": avg_cost,
        "records": [
            {
                "id": r.id,
                "remaining_quantity": r.remaining_quantity,
                "product_cost": r.product_cost,
                "warehouse_type": r.warehouse_type,
                "inbound_at": r.inbound_at
            }
            for r in records
        ]
    }
