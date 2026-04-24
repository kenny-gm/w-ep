from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import json
from app.database import get_db
from app.models.models import Alert, User, OperationLog, Product
from app.routers.auth import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/alerts", tags=["预警"])

class AlertProcess(BaseModel):
    action_type: str
    content: str
    tracking_days: int = 7
    title: Optional[str] = None
    action_detail: Optional[dict] = None

def get_user_allowed_owners(user, db: Session) -> list:
    if user.role == "admin":
        return []
    allowed = user.allowed_owners or []
    if isinstance(allowed, str):
        try:
            allowed = json.loads(allowed)
        except:
            allowed = []
    return allowed

def filter_alerts_by_owner(query, user, db: Session):
    allowed_owners = get_user_allowed_owners(user, db)
    
    if not allowed_owners:
        return query
    
    owner_products = db.query(Product.id).filter(
        Product.owner.in_(allowed_owners)
    ).all()
    product_ids = [p[0] for p in owner_products]
    
    if not product_ids:
        return query.filter(Alert.id == -1)
    
    return query.filter(Alert.product_id.in_(product_ids))

@router.get("/unread")
def get_unread_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Alert).filter(Alert.is_read == False)
    query = filter_alerts_by_owner(query, current_user, db)
    alerts = query.order_by(Alert.created_at.desc()).all()
    return alerts

@router.get("/")
def get_alerts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Alert)
    query = filter_alerts_by_owner(query, current_user, db)
    total = query.count()
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": alerts}

@router.put("/{alert_id}/read")
def mark_as_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    
    query = db.query(Alert).filter(Alert.id == alert_id)
    query = filter_alerts_by_owner(query, current_user, db)
    alert = query.first()
    if not alert:
        raise HTTPException(status_code=403, detail="无权限操作")
    
    alert.is_read = True
    db.commit()
    return {"message": "已标记为已读"}

@router.post("/{alert_id}/process")
def process_alert(
    alert_id: int,
    data: AlertProcess,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Alert).filter(Alert.id == alert_id)
    query = filter_alerts_by_owner(query, current_user, db)
    alert = query.first()
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    if alert.is_resolved:
        raise HTTPException(status_code=400, detail="预警已处理")

    log = OperationLog(
        user_id=current_user.id,
        product_id=alert.product_id,
        shop_id=None,
        log_date=datetime.now().strftime("%Y-%m-%d"),
        action_type=data.action_type,
        action_detail=data.action_detail or {},
        metrics_before=alert.metric_snapshot,
        effect_tracking_days=data.tracking_days,
        title=data.title or f"处理预警：{alert.title}",
        content=data.content,
        alert_id=alert.id
    )
    db.add(log)
    db.flush()

    alert.is_resolved = True
    alert.resolved_note = data.content
    alert.resolved_at = datetime.now()
    alert.operation_log_id = log.id
    db.commit()

    return {"message": "预警已处理，已创建运营日志", "operation_log_id": log.id}
