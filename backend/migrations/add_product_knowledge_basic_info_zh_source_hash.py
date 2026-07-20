"""
Migration: track which WB basic info generated product_knowledge.basic_info_zh.

This keeps Chinese basic info stable after it has been generated once. The
system only regenerates it when the WB/Russian basic-info source changes.
"""
from sqlalchemy import text

from app.database import engine


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    dialect = engine.dialect.name
    if dialect == "mysql":
        row = conn.execute(text("""
            SELECT COUNT(*) AS cnt
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :table_name
              AND COLUMN_NAME = :column_name
        """), {"table_name": table_name, "column_name": column_name}).fetchone()
        return bool(row and row[0])
    if dialect == "sqlite":
        rows = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
        return any(row[1] == column_name for row in rows)
    raise RuntimeError(f"Unsupported dialect: {dialect}")


def migrate_add_product_knowledge_basic_info_zh_source_hash() -> bool:
    with engine.begin() as conn:
        if _column_exists(conn, "product_knowledge", "basic_info_zh_source_hash"):
            print("[migration] product_knowledge.basic_info_zh_source_hash 已存在，跳过")
            return True
        conn.execute(text("ALTER TABLE product_knowledge ADD COLUMN basic_info_zh_source_hash VARCHAR(64) DEFAULT ''"))
        print("[migration] product_knowledge.basic_info_zh_source_hash 已添加")
    return True


if __name__ == "__main__":
    success = migrate_add_product_knowledge_basic_info_zh_source_hash()
    exit(0 if success else 1)
