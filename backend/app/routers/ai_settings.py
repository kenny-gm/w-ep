"""
AI 大模型设置路由

GET  - 查看当前 AI 配置（不含 API Key）
PATCH - 更新 AI 配置（不含 Key）
POST /test - 测试 AI 连接
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import SystemSetting
from app.routers.auth import get_current_user, get_current_admin
from app.services.ai_client import AIClient


router = APIRouter(prefix="/api/ai-settings", tags=["AI设置"])


# ========== Schema ==========

class AISettingsPatch(BaseModel):
    enabled: Optional[bool] = None
    provider: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    timeout: Optional[int] = None
    max_tokens: Optional[int] = None
    # 禁止接收 API Key 字段
    api_key: Optional[str] = None

    @validator("api_key")
    def reject_api_key(cls, v):
        if v is not None:
            raise ValueError("API Key 不能通过此接口提交，请通过环境变量配置")
        return v

    class Config:
        extra = "forbid"


# ========== 接口 ==========

@router.get("")
def get_ai_settings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    """查看 AI 配置（admin/manager）"""
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="权限不足")
    client = AIClient(db)
    cfg = client.get_effective_config()
    return cfg


@router.patch("")
def patch_ai_settings(
    data: AISettingsPatch,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    """更新 AI 配置（仅 admin）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    if data.api_key is not None:
        pass  # 静默忽略

    updates = {
        "ai.enabled": str(data.enabled).lower() if data.enabled is not None else None,
        "ai.provider": data.provider if data.provider is not None else None,
        "ai.base_url": data.base_url if data.base_url is not None else None,
        "ai.model": data.model if data.model is not None else None,
        "ai.timeout": str(data.timeout) if data.timeout is not None else None,
        "ai.max_tokens": str(data.max_tokens) if data.max_tokens is not None else None,
    }
    updates = {k: v for k, v in updates.items() if v is not None}

    for key, value in updates.items():
        row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if row:
            row.value = value
    db.commit()
    client = AIClient(db)
    return client.get_effective_config()


@router.post("/test")
def test_ai_connection(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    """测试 AI 连接（admin/manager）"""
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="权限不足")
    client = AIClient(db)
    result = client.test_connection()
    return result
