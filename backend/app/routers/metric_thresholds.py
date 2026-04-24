"""
指标阈值设置路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.metric_threshold import MetricThreshold
from app.routers.auth import get_current_admin, get_current_user

router = APIRouter(prefix="/api/metric-thresholds", tags=["指标设置"])


# Pydantic模型
class MetricThresholdCreate(BaseModel):
    metric_name: str
    display_name: str
    warning_threshold: float
    danger_threshold: Optional[float] = None
    comparison: str = "less_than"  # less_than, greater_than
    good_color: str = "#67c23a"
    warning_color: str = "#e6a23c"
    danger_color: str = "#f56c6c"
    is_active: bool = True


class MetricThresholdUpdate(BaseModel):
    display_name: Optional[str] = None
    warning_threshold: Optional[float] = None
    danger_threshold: Optional[float] = None
    comparison: Optional[str] = None
    good_color: Optional[str] = None
    warning_color: Optional[str] = None
    danger_color: Optional[str] = None
    is_active: Optional[bool] = None


class MetricThresholdResponse(BaseModel):
    id: int
    metric_name: str
    display_name: str
    warning_threshold: float
    danger_threshold: Optional[float]
    comparison: str
    good_color: str
    warning_color: str
    danger_color: str
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[MetricThresholdResponse])
def list_thresholds(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取所有指标阈值配置"""
    thresholds = db.query(MetricThreshold).all()
    return thresholds


@router.post("/", response_model=MetricThresholdResponse)
def create_threshold(
    threshold: MetricThresholdCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建指标阈值配置"""
    # 检查是否已存在
    existing = db.query(MetricThreshold).filter(
        MetricThreshold.metric_name == threshold.metric_name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该指标配置已存在")
    
    db_threshold = MetricThreshold(**threshold.dict())
    db.add(db_threshold)
    db.commit()
    db.refresh(db_threshold)
    
    return db_threshold


@router.put("/{metric_name}/", response_model=MetricThresholdResponse)
def update_threshold(
    metric_name: str,
    threshold: MetricThresholdUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新指标阈值配置"""
    db_threshold = db.query(MetricThreshold).filter(
        MetricThreshold.metric_name == metric_name
    ).first()
    
    if not db_threshold:
        raise HTTPException(status_code=404, detail="指标配置不存在")
    
    # 更新字段
    for key, value in threshold.dict(exclude_unset=True).items():
        setattr(db_threshold, key, value)
    
    db.commit()
    db.refresh(db_threshold)
    
    return db_threshold


@router.delete("/{metric_name}/")
def delete_threshold(
    metric_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除指标阈值配置（硬删除）"""
    db_threshold = db.query(MetricThreshold).filter(
        MetricThreshold.metric_name == metric_name
    ).first()
    
    if not db_threshold:
        raise HTTPException(status_code=404, detail="指标配置不存在")
    
    db.delete(db_threshold)
    db.commit()
    
    return {"message": "已删除"}


@router.get("/{metric_name}/", response_model=MetricThresholdResponse)
def get_threshold(
    metric_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取单个指标阈值配置"""
    threshold = db.query(MetricThreshold).filter(
        MetricThreshold.metric_name == metric_name,
        MetricThreshold.is_active == True
    ).first()
    
    if not threshold:
        raise HTTPException(status_code=404, detail="指标配置不存在")
    
    return threshold


@router.post("/init-defaults/")
def init_default_thresholds(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """初始化默认指标阈值配置"""
    defaults = [
        {
            "metric_name": "roas",
            "display_name": "ROAS",
            "warning_threshold": 3.0,
            "danger_threshold": 2.0,
            "comparison": "less_than",
            "good_color": "#67c23a",
            "warning_color": "#e6a23c",
            "danger_color": "#f56c6c"
        },
        {
            "metric_name": "acos",
            "display_name": "ACOS",
            "warning_threshold": 0.10,  # 10%
            "danger_threshold": 0.20,   # 20%
            "comparison": "greater_than",
            "good_color": "#67c23a",
            "warning_color": "#e6a23c",
            "danger_color": "#f56c6c"
        },
        {
            "metric_name": "ctr",
            "display_name": "广告点击率",
            "warning_threshold": 0.03,  # 3%
            "danger_threshold": 0.02,   # 2%
            "comparison": "less_than",
            "good_color": "#67c23a",
            "warning_color": "#e6a23c",
            "danger_color": "#f56c6c"
        },
        {
            "metric_name": "natural_orders_ratio",
            "display_name": "自然订单占比",
            "warning_threshold": 0.50,  # 50%
            "danger_threshold": 0.30,   # 30%
            "comparison": "less_than",
            "good_color": "#67c23a",
            "warning_color": "#e6a23c",
            "danger_color": "#f56c6c"
        }
    ]
    
    created_count = 0
    for default in defaults:
        existing = db.query(MetricThreshold).filter(
            MetricThreshold.metric_name == default["metric_name"]
        ).first()
        
        if not existing:
            db_threshold = MetricThreshold(**default)
            db.add(db_threshold)
            created_count += 1
    
    db.commit()
    
    return {"message": f"已初始化 {created_count} 个默认配置"}
