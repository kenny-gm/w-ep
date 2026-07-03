"""
迁移：新增 sync_locks 表，用于客服同步分布式锁
"""
from sqlalchemy import text
from app.database import engine


def migrate_add_sync_locks():
    """幂等迁移：检查表是否存在，不存在则创建"""
    with engine.connect() as conn:
        # 检查表是否已存在
        result = conn.execute(text("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='sync_locks'
        """))
        if result.fetchone():
            print("[迁移] sync_locks 表已存在，跳过")
            return
        
        conn.execute(text("""
            CREATE TABLE sync_locks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lock_key TEXT NOT NULL UNIQUE,
                locked_by TEXT NOT NULL,
                locked_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("CREATE INDEX idx_sync_locks_key ON sync_locks(lock_key)"))
        conn.execute(text("CREATE INDEX idx_sync_locks_expires ON sync_locks(expires_at)"))
        conn.commit()
        print("[迁移] sync_locks 表创建成功")


if __name__ == "__main__":
    migrate_add_sync_locks()
