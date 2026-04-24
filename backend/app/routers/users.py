from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import bcrypt
from datetime import datetime

from app.database import get_db
from app.models.models import User
from app.routers.auth import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["admin-users"])


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    allowed_owners: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    allowed_owners: Optional[List[str]] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    allowed_owners: Optional[List[str]] = None


@router.get("/users/", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """获取用户列表"""
    users = db.query(User).order_by(User.id).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """获取单个用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/users/")
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """创建用户"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    new_user = User(
        username=user.username,
        password_hash=password_hash,
        role=user.role.upper(),
        allowed_owners=",".join(user.allowed_owners) if user.allowed_owners else None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"id": new_user.id, "username": new_user.username, "role": new_user.role}


@router.put("/users/{user_id}/")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.role is not None:
        user.role = user_update.role.upper()
    if user_update.allowed_owners is not None:
        user.allowed_owners = ",".join(user_update.allowed_owners)
    
    db.commit()
    return {"message": "用户更新成功"}


@router.post("/users/{user_id}/reset-password/")
async def reset_password(
    user_id: int,
    new_password: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """重置密码"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    db.commit()
    
    return {"message": "密码重置成功"}


@router.delete("/users/{user_id}/")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户删除成功"}
