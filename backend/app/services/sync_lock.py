"""
客服同步分布式锁服务

使用数据库表实现分布式锁，支持：
- 同一 shop_id 同一时间只允许一个同步运行
- 锁过期机制，防止异常后永久锁死
- 幂等获取锁（已存在且未过期则返回失败）
"""
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.config import settings


LOCK_TTL_SECONDS = 600  # 10分钟锁过期


class SyncLockService:
    """DB-based distributed lock for customer service sync operations."""

    def __init__(self, db: Session):
        self.db = db
        self.lock_key: Optional[str] = None
        self.lock_value: str = f"worker-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    def acquire(self, shop_id: int, sync_type: str = "customer_service") -> bool:
        """
        尝试获取锁。
        返回 True 表示获取成功，False 表示已有其他同步运行。
        """
        self.lock_key = f"cs_sync:{shop_id}:{sync_type}"
        now = datetime.now()
        expires_at = now + timedelta(seconds=LOCK_TTL_SECONDS)

        # 先清理过期锁
        self.db.execute(
            text("DELETE FROM sync_locks WHERE lock_key = :lock_key AND expires_at < :now"),
            {"lock_key": self.lock_key, "now": now}
        )

        # 尝试插入新锁（ON CONFLICT 不存在，靠 UNIQUE 约束保证）
        try:
            self.db.execute(
                text("""
                    INSERT INTO sync_locks (lock_key, locked_by, locked_at, expires_at)
                    VALUES (:lock_key, :locked_by, :locked_at, :expires_at)
                """),
                {
                    "lock_key": self.lock_key,
                    "locked_by": self.lock_value,
                    "locked_at": now,
                    "expires_at": expires_at,
                }
            )
            self.db.commit()
            return True
        except Exception:
            # 锁已被占用（或 UNIQUE 冲突）
            self.db.rollback()
            return False

    def release(self) -> None:
        """释放自己持有的锁"""
        if not self.lock_key:
            return
        try:
            self.db.execute(
                text("DELETE FROM sync_locks WHERE lock_key = :lock_key AND locked_by = :locked_by"),
                {"lock_key": self.lock_key, "locked_by": self.lock_value}
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
        finally:
            self.lock_key = None

    def is_locked(self, shop_id: int, sync_type: str = "customer_service") -> bool:
        """检查是否有活跃锁（不区分是谁的锁）"""
        lock_key = f"cs_sync:{shop_id}:{sync_type}"
        now = datetime.now()
        result = self.db.execute(
            text("SELECT COUNT(*) FROM sync_locks WHERE lock_key = :lock_key AND expires_at > :now"),
            {"lock_key": lock_key, "now": now}
        )
        return result.fetchone()[0] > 0

    @contextmanager
    def hold(self, shop_id: int, sync_type: str = "customer_service"):
        """上下文管理器：获取锁，执行逻辑，自动释放"""
        acquired = self.acquire(shop_id, sync_type)
        try:
            yield acquired
        finally:
            if acquired:
                self.release()


def run_with_cs_sync_lock(shop_id: int, sync_type: str, func, *args, **kwargs):
    """
    在锁保护下执行函数。
    如果获取锁失败，返回 {"locked": True}
    如果获取锁成功，执行 func(*args, **kwargs)，执行完自动释放锁
    """
    db = SessionLocal()
    try:
        lock = SyncLockService(db)
        acquired = lock.acquire(shop_id, sync_type)
        if not acquired:
            return {"locked": True}
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            lock.release()
    finally:
        db.close()
