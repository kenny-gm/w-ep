"""
Migration: 添加用户细粒度权限字段
- users.permissions   (JSON)  客服权限码数组
- users.allowed_shops (JSON)  可访问店铺ID列表

幂等：列存在则跳过。
"""
import sys
sys.path.insert(0, "/app/backend")

from app.database import engine, Base


def run():
    with engine.connect() as conn:
        # permissions 列
        try:
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN permissions JSON DEFAULT '[]'")
            print("✓ users.permissions 列已添加")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("✓ users.permissions 列已存在，跳过")
            else:
                print(f"? users.permissions: {e}")

        # allowed_shops 列
        try:
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN allowed_shops JSON DEFAULT '[]'")
            print("✓ users.allowed_shops 列已添加")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print("✓ users.allowed_shops 列已存在，跳过")
            else:
                print(f"? users.allowed_shops: {e}")


if __name__ == "__main__":
    run()
