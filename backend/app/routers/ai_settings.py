"""
AI 大模型设置路由

GET  - 查看当前 AI 配置（不含 API Key 明文）
PATCH - 更新 AI 配置（admin 可更新加密 API Key）
POST /test - 测试 AI 连接
DELETE /api-key - 删除后台存储的加密 API Key（admin only）
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import SystemSetting
from app.routers.auth import get_current_user, get_current_admin
from app.services.ai_client import AIClient
from app.services.secret_crypto import encrypt_secret


router = APIRouter(prefix="/api/ai-settings", tags=["AI设置"])


# ========== Schema ==========

class AISettingsPatch(BaseModel):
    enabled: Optional[bool] = None
    provider: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    timeout: Optional[int] = None
    max_tokens: Optional[int] = None
    # admin 可选传入 api_key，非空时加密存储
    api_key: Optional[str] = Field(None, description="留空则不修改当前 API Key")

    class Config:
        extra = "forbid"


class ApiKeyOperationResponse(BaseModel):
    success: bool
    api_key_configured: bool
    api_key_source: str


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
    return client.get_effective_config()


@router.patch("")
def patch_ai_settings(
    data: AISettingsPatch,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    """更新 AI 配置（仅 admin）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")

    # 处理 API Key：仅非空字符串才更新
    if data.api_key:
        encrypted = encrypt_secret(data.api_key)
        row = db.query(SystemSetting).filter(SystemSetting.key == "ai.api_key_encrypted").first()
        if row:
            row.value = encrypted
        else:
            db.add(SystemSetting(key="ai.api_key_encrypted", value=encrypted))
        db.commit()

    # 处理其他配置
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
        else:
            db.add(SystemSetting(key=key, value=value))
    db.commit()

    client = AIClient(db)
    result = client.get_effective_config()
    return result


@router.delete("/api-key", response_model=ApiKeyOperationResponse)
def delete_api_key(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    """删除后台存储的加密 API Key（仅 admin）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")

    row = db.query(SystemSetting).filter(SystemSetting.key == "ai.api_key_encrypted").first()
    if row:
        db.delete(row)
        db.commit()

    client = AIClient(db)
    info = client.get_api_key_info()
    return ApiKeyOperationResponse(
        success=True,
        api_key_configured=info["api_key_configured"],
        api_key_source=info["api_key_source"],
    )


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