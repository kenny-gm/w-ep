"""
Migration: 修复 ad_records 唯一索引，包含 advert_id

解决 WB 广告同一产品同一天多个 advert_id 时的 UNIQUE constraint 冲突。

索引变更：(shop_id, product_id, DATE(record_date), ad_type)
       → (shop_id, product_id, DATE(record_date), ad_type, advert_id)

幂等：可重复执行，重复执行时跳过已符合目标的索引。
"""

from sqlalchemy import text
from app.database import engine


def migrate_fix_ad_records_dedup_index():
    """
    修复 ad_records.ix_ad_records_dedup 唯一索引，使其包含 advert_id。
    
    执行逻辑（幂等）：
    1. advert_id NULL → 0
    2. 检查新索引 key 下是否有重复（禁止静默破坏）
    3. 如有重复，报错并列出重复记录
    4. 如无重复，创建新索引
    5. 验证索引定义
    
    Returns:
        bool: True = 迁移成功或已符合目标, False = 有重复数据/执行失败
    """
    with engine.connect() as conn:
        # ============================================================
        # Step 1: advert_id NULL → 0
        # ============================================================
        result = conn.execute(text("SELECT COUNT(*) FROM ad_records WHERE advert_id IS NULL"))
        null_count = result.fetchone()[0]
        if null_count > 0:
            print(f"[migration] advert_id NULL → 0: {null_count} 条")
            conn.execute(text("UPDATE ad_records SET advert_id = 0 WHERE advert_id IS NULL"))
            conn.commit()
        else:
            print("[migration] advert_id NULL 检查: 0 条，无需处理")

        # ============================================================
        # Step 2: 读取当前索引定义
        # ============================================================
        result = conn.execute(text(
            "SELECT sql FROM sqlite_master WHERE type='index' AND name='ix_ad_records_dedup'"
        ))
        row = result.fetchone()
        current_sql = row[0] if row else None

        if current_sql and "advert_id" in current_sql:
            print("[migration] 索引已包含 advert_id，跳过")
            return True

        # ============================================================
        # Step 3: 检查新索引 key 下是否有重复
        # ============================================================
        dupes_result = conn.execute(text("""
            SELECT
                shop_id,
                product_id,
                DATE(record_date) AS dt,
                ad_type,
                advert_id,
                COUNT(*) AS cnt
            FROM ad_records
            GROUP BY shop_id, product_id, DATE(record_date), ad_type, advert_id
            HAVING COUNT(*) > 1
        """))
        dupes = dupes_result.fetchall()

        if dupes:
            print("[migration] ❌ 发现重复数据，无法创建索引：")
            for d in dupes:
                print(f"  shop={d[0]} pid={d[1]} dt={d[2]} type={d[3]} advert={d[4]} cnt={d[5]}")
            print("[migration] 必须先手动处理重复数据后再执行此迁移")
            return False

        print("[migration] 重复数据检查: 0 组，通过")

        # ============================================================
        # Step 4: 删除旧索引，创建新索引
        # ============================================================
        conn.execute(text("DROP INDEX IF EXISTS ix_ad_records_dedup"))
        conn.commit()
        print("[migration] 旧索引已删除")

        conn.execute(text("""
            CREATE UNIQUE INDEX ix_ad_records_dedup
            ON ad_records(shop_id, product_id, DATE(record_date), ad_type, advert_id)
        """))
        conn.commit()
        print("[migration] 新索引创建成功")

        # ============================================================
        # Step 5: 验证索引定义
        # ============================================================
        result = conn.execute(text(
            "SELECT sql FROM sqlite_master WHERE type='index' AND name='ix_ad_records_dedup'"
        ))
        new_sql = result.fetchone()[0]
        print(f"[migration] 索引验证: {new_sql}")

        expected = "CREATE UNIQUE INDEX ix_ad_records_dedup ON ad_records(shop_id, product_id, DATE(record_date), ad_type, advert_id)"
        if new_sql != expected:
            print(f"[migration] ❌ 索引验证失败，期望: {expected}")
            return False

        print("[migration] ✅ 迁移完成")
        return True


if __name__ == "__main__":
    success = migrate_fix_ad_records_dedup_index()
    exit(0 if success else 1)