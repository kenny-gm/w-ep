"""
Migration: 补全 customer_service_items 缺失列

初始表创建时模型不完整，导致大量列缺失：
- 初始只有 11 列（buyer_key/reply_sign 是之前 migration 加的）
- 模型实际需要所有核心业务列

幂等：检查列是否存在再 ADD COLUMN。
"""

from sqlalchemy import text
from app.database import engine


def migrate_fix_customer_service_items_columns():
    with engine.connect() as conn:
        # Step 1: 检查表是否存在
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='customer_service_items'"
        ))
        if not result.fetchone():
            print("[migration] customer_service_items 表不存在，跳过")
            return True

        # Step 2: 检查现有列
        col_result = conn.execute(text("PRAGMA table_info(customer_service_items)"))
        existing_cols = {row[1] for row in col_result.fetchall()}

        # Step 3: 需要添加的列（从 models.py 模型提取）
        # (列名, 默认值/SQL 类型)
        # 分两批：常量默认值 和 需要触发了来设置默认值的列
        # SQLite ADD COLUMN 只支持恒定默认值，CURRENT_TIMESTAMP 是函数不允许
        cols_constant = [
            ("external_status", "TEXT"),
            ("product_id", "INTEGER"),
            ("nm_id", "TEXT"),
            ("sku", "TEXT"),
            ("product_name", "TEXT"),
            ("product_name_ru", "TEXT"),
            ("owner", "TEXT"),
            ("product_matched", "INTEGER DEFAULT 0"),
            ("assigned_owner", "TEXT"),
            ("assigned_user_id", "INTEGER"),
            ("assignment_status", "TEXT DEFAULT 'unassigned'"),
            ("handover_note", "TEXT DEFAULT ''"),
            ("rating", "INTEGER"),
            ("status", "TEXT DEFAULT 'open'"),
            ("reply_status", "TEXT DEFAULT 'unanswered'"),
            ("priority", "TEXT DEFAULT 'normal'"),
            ("risk_level", "TEXT DEFAULT 'normal'"),
            ("issue_type", "TEXT DEFAULT 'other'"),
            ("is_viewed", "INTEGER DEFAULT 0"),
            ("is_archived", "INTEGER DEFAULT 0"),
            ("first_replied_by", "TEXT"),
            ("first_replied_at", "TIMESTAMP"),
            ("last_handled_by", "TEXT"),
            ("last_handled_at", "TIMESTAMP"),
            ("closed_by", "TEXT"),
            ("closed_at", "TIMESTAMP"),
            ("external_created_at", "TIMESTAMP"),
            ("external_updated_at", "TIMESTAMP"),
            ("sla_deadline_at", "TIMESTAMP"),
            ("is_overdue", "INTEGER DEFAULT 0"),
            ("return_deadline_hours", "INTEGER DEFAULT 120"),
            ("created_at", "TIMESTAMP"),  # CURRENT_TIMESTAMP 在 SQLite ADD COLUMN 不允许，后续 UPDATE
            ("updated_at", "TIMESTAMP"),  # 同上
        ]

        added = []
        for col_name, col_def in cols_constant:
            if col_name not in existing_cols:
                conn.execute(text(f"ALTER TABLE customer_service_items ADD COLUMN {col_name} {col_def}"))
                added.append(col_name)
                print(f"[migration] 添加列: {col_name}")
            else:
                print(f"[migration] 列已存在: {col_name}")

        conn.commit()

        # created_at / updated_at 在 SQLite ADD COLUMN 不支持 DEFAULT CURRENT_TIMESTAMP
        # 手动 UPDATE 已有记录（后续 INSERT 时数据库会自动设值，但 SQLite 无触发器支持 INSERT 的 DEFAULT）
        for col, val in [("created_at", "datetime('now')"), ("updated_at", "datetime('now')")]:
            if col not in existing_cols:
                try:
                    conn.execute(text(f"UPDATE customer_service_items SET {col} = {val} WHERE {col} IS NULL"))
                    conn.commit()
                    print(f"[migration] 回填 {col} 完成")
                except Exception as e:
                    print(f"[migration] 回填 {col} 失败: {e}")

        if added:
            print(f"[migration] ✅ 补全完成，新增 {len(added)} 列")
        else:
            print("[migration] ✅ 所有列已存在，无需修改")

        # Step 4: 验证
        verify_result = conn.execute(text("PRAGMA table_info(customer_service_items)"))
        final_cols = {row[1] for row in verify_result.fetchall()}
        missing = set(c for c, _ in cols_constant) - final_cols
        if missing:
            print(f"[migration] ⚠️ 仍有缺失列: {missing}")
        else:
            print(f"[migration] ✅ 验证通过，总列数: {len(final_cols)}")

        return True


if __name__ == "__main__":
    success = migrate_fix_customer_service_items_columns()
    exit(0 if success else 1)
