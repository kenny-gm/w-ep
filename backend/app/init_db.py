"""初始化数据库表"""
from app.database import Base, engine
from app.models import models  # 导入整个模块

# 创建所有表
Base.metadata.create_all(bind=engine)
print("数据库表创建完成!")

# 列出所有表
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"创建的表: {tables}")


# ============================================================
# 迁移：确保 platform_config 列存在
# ============================================================
def migrate_add_platform_config(db_url: str = None):
    """检测并添加 platform_config 列（如果不存在）"""
    if db_url is None:
        # 从 engine 获取连接字符串
        db_url = str(engine.url)

    from sqlalchemy import text
    with engine.connect() as conn:
        # 检测列是否存在
        try:
            result = conn.execute(text("PRAGMA table_info(shops)"))
            columns = [row[1] for row in result.fetchall()]
        except Exception as e:
            print(f"检测 shops 表结构失败: {e}")
            return False

        if "platform_config" not in columns:
            print("检测到 shops 表缺少 platform_config 列，执行 ALTER ...")
            try:
                # SQLite / PostgreSQL 兼容
                if "postgres" in db_url.lower():
                    conn.execute(text(
                        "ALTER TABLE shops ADD COLUMN platform_config JSON DEFAULT '{}'"
                    ))
                else:
                    # SQLite
                    conn.execute(text(
                        "ALTER TABLE shops ADD COLUMN platform_config TEXT DEFAULT '{}'"
                    ))
                conn.commit()
                print("platform_config 列添加成功")
                return True
            except Exception as e:
                print(f"添加 platform_config 列失败: {e}")
                return False
        else:
            print("platform_config 列已存在，跳过")
            return True


# 自动执行迁移
migrate_add_platform_config()