"""
客服权限系统

规则：
- admin → 全部权限，全部数据范围
- customer_service → 全部 customer_service:* + permissions 额外权限，数据范围 allowed_shops/allowed_owners
- product_owner → permissions 或全部 customer_service:*（permissions为空时），数据范围 allowed_owners（必须，非空则无数据）
- manager/custom → 完全按 permissions，不默认客服写权限
- viewer → customer_service:read
- STAFF → customer_service:read（升级兼容）
"""
from __future__ import annotations

import json
from typing import Any, List, Optional, Set

from app.models.models import User


# ── 客服权限码 ──────────────────────────────────────────────
CS_ALL_PERMS = {
    "customer_service:read",
    "customer_service:sync",
    "customer_service:translate",
    "customer_service:ai_draft",
    "customer_service:note",
    "customer_service:status",
    "customer_service:reply_feedback",
    "customer_service:answer_question",
    "customer_service:reject_question",
    "customer_service:send_chat",
    "customer_service:handle_return",
    "customer_service:admin",
}


# ── 解析工具 ────────────────────────────────────────────────

def parse_json_list(value: Any) -> List[Any]:
    """兼容多种格式返回 list"""
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    if isinstance(value, str):
        if not value.strip():
            return []
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return [v.strip() for v in value.split(",") if v.strip()]
    return []


def _role(user: User) -> str:
    """获取用户的角色字符串（小写），兼容 Enum 或纯字符串"""
    raw = getattr(user, "role", "") or ""
    return getattr(raw, "value", str(raw).lower()).lower()


def _user_permissions_list(user: User) -> List[str]:
    """读取 user.permissions 字段并返回 list"""
    raw = getattr(user, "permissions", None)
    return parse_json_list(raw)


def _user_allowed_shops(user: User) -> List[int]:
    """读取 user.allowed_shops 并返回 int list"""
    raw = getattr(user, "allowed_shops", None)
    vals = parse_json_list(raw)
    return [int(v) for v in vals if str(v).isdigit()]


def _user_allowed_owners(user: User) -> List[str]:
    """读取 user.allowed_owners 并返回 str list"""
    raw = getattr(user, "allowed_owners", None)
    return [str(v) for v in parse_json_list(raw) if v]


# ── 权限计算 ────────────────────────────────────────────────

def get_user_permissions(user: User) -> Set[str]:
    """
    返回用户所有有效权限码集合。

    规则：
    - admin → {"*"}
    - customer_service → CS_ALL_PERMS | user.permissions
    - product_owner → user.permissions or CS_ALL_PERMS（permissions为空时默认全客服权限）
    - viewer → {"customer_service:read"}
    - manager/custom → user.permissions（可为空）
    - STAFF → {"customer_service:read"}（升级兼容）
    """
    role = _role(user)

    if role == "admin":
        return {"*"}

    perms = set(_user_permissions_list(user))

    if role == "customer_service":
        return CS_ALL_PERMS | perms

    if role == "product_owner":
        # permissions 为空时默认给全部客服权限（数据范围由 allowed_owners 控制）
        if not perms:
            return CS_ALL_PERMS | perms
        return perms

    if role == "viewer":
        return {"customer_service:read"}

    # manager / custom / staff：完全按 permissions 字段
    # staff 兼容：默认只有 read
    if role == "staff" and not perms:
        return {"customer_service:read"}

    return perms


# ── 权限判断 ────────────────────────────────────────────────

def has_permission(user: User, perm: str) -> bool:
    """
    判断用户是否有指定权限。

    - admin / "*" → 全部放行
    - 精确匹配
    - 支持通配符 "customer_service:*" → 任意 customer_service:xxx
    """
    perms = get_user_permissions(user)

    if "*" in perms:
        return True

    if perm in perms:
        return True

    # 通配符支持：仅当被检查的 perm 本身以 "*" 结尾时（如 "customer_service:*"）
    if perm.endswith("*"):
        prefix = perm.rstrip("*:") + ":"
        if any(p.startswith(prefix) for p in perms):
            return True

    return False


def require_permission(user: User, perm: str) -> None:
    """无权限时抛出 403。"""
    if not has_permission(user, perm):
        raise PermissionError(f"缺少权限: {perm}")


def require_cs_permission(user: User, perm: str) -> None:
    """客服权限检查，403 转 HTTPException。"""
    try:
        require_permission(user, perm)
    except PermissionError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail=str(e))


# ── 数据范围 ────────────────────────────────────────────────

def can_access_customer_item(user: User, item: "CustomerServiceItem") -> bool:
    """
    判断用户能否访问某条客服事项。

    - admin / customer_service:admin → 不过滤
    - allowed_shops 非空 → item.shop_id 必须在列表
    - allowed_owners 非空 → item.owner 或 item.assigned_owner 必须在列表
    - product_owner allowed_owners 为空 → 不能访问全量（返回 False）
    - customer_service allowed_shops/allowed_owners 都为空 → 可看全部
    """
    role = _role(user)

    if role == "admin":
        return True

    # customer_service:admin 跳过后续检查
    if has_permission(user, "customer_service:admin"):
        return True

    # allowed_shops 检查
    shops = _user_allowed_shops(user)
    if shops:
        if item.shop_id not in shops:
            return False

    # allowed_owners 检查
    owners = _user_allowed_owners(user)
    role_name = _role(user)

    if owners:
        # 非 customer_service 角色，allowed_owners 限制严格
        if role_name not in ("customer_service",):
            item_owner = getattr(item, "owner", None) or ""
            item_assigned = getattr(item, "assigned_owner", None) or ""
            if str(item_owner) not in owners and str(item_assigned) not in owners:
                return False
        else:
            # customer_service 角色：owner 限制
            item_owner = getattr(item, "owner", None) or ""
            item_assigned = getattr(item, "assigned_owner", None) or ""
            if str(item_owner) not in owners and str(item_assigned) not in owners:
                return False
    else:
        # allowed_owners 为空
        if role_name == "product_owner":
            # product_owner 无 allowed_owners → 不能看全量
            return False
        # customer_service allowed_owners 为空 → 可看全部（已在上层返回）

    return True


def filter_customer_query(user: User, query) -> Any:
    """
    对 SQLAlchemy query 追加数据范围过滤条件。
    返回新的 query 对象（不修改原 query）。
    """
    from app.models.models import CustomerServiceItem
    from sqlalchemy import or_

    role = _role(user)

    if role == "admin":
        return query

    if has_permission(user, "customer_service:admin"):
        return query

    shops = _user_allowed_shops(user)
    owners = _user_allowed_owners(user)

    conditions = []

    if shops:
        conditions.append(CustomerServiceItem.shop_id.in_(shops))

    if owners:
        conditions.append(
            or_(
                CustomerServiceItem.owner.in_(owners),
                CustomerServiceItem.assigned_owner.in_(owners),
            )
        )
    elif role == "product_owner":
        # product_owner 无 allowed_owners → 只返回空结果（加一个永远为假的条件）
        conditions.append(CustomerServiceItem.id == -1)

    if conditions:
        return query.filter(or_(*conditions))

    return query
