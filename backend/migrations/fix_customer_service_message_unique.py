"""
迁移：为 customer_service_messages 增加唯一约束 (item_id, external_message_id)
并清理历史重复数据

前置条件：无
"""
from sqlalchemy import text
from app.database import engine


def migrate_fix_customer_service_message_unique():
    with engine.connect() as conn:
        # 1. 检查表是否存在
        result = conn.execute(text("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='customer_service_messages'
        """))
        if not result.fetchone():
            print("[迁移] customer_service_messages 表不存在，跳过")
            return

        # 2. 检查唯一约束是否已存在
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='ix_customer_service_message_unique'
        """))
        if result.fetchone():
            print("[迁移] ix_customer_service_message_unique 索引已存在，跳过")
            return

        # 3. 查找重复数据
        result = conn.execute(text("""
            SELECT item_id, external_message_id, COUNT(*) as cnt, MIN(id) as keep_id
            FROM customer_service_messages
            WHERE external_message_id IS NOT NULL AND external_message_id != ''
            GROUP BY item_id, external_message_id
            HAVING COUNT(*) > 1
        """))
        duplicates = result.fetchall()
        if duplicates:
            print(f"[迁移] 发现 {len(duplicates)} 组重复消息，开始清理...")
            for dup in duplicates:
                item_id, ext_id, cnt, keep_id = dup
                # 删除重复，保留 id 最小的一条
                conn.execute(text("""
                    DELETE FROM customer_service_messages
                    WHERE item_id = :item_id 
                    AND external_message_id = :ext_id
                    AND id != :keep_id
                """), {"item_id": item_id, "ext_id": ext_id, "keep_id": keep_id})
            conn.commit()
            print(f"[迁移] 清理完成，删除了 {sum(d[2] - 1 for d in duplicates)} 条重复消息")

        # 4. 创建唯一索引
        conn.execute(text("""
            CREATE UNIQUE INDEX ix_customer_service_message_unique 
            ON customer_service_messages(item_id, external_message_id)
        """))
        conn.commit()
        print("[迁移] ix_customer_service_message_unique 唯一索引创建成功")


if __name__ == "__main__":
    migrate_fix_customer_service_message_unique()
