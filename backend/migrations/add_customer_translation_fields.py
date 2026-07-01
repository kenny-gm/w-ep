"""
Migration: 新增客服翻译字段（幂等）

customer_service_items: content_zh, title_zh, translation_status, translated_at, translation_error, translation_source_hash
customer_service_messages: message_text_zh, translation_status, translated_at, translation_error, translation_source_hash
"""
from sqlalchemy import text
from app.database import engine


def _column_exists(conn, table_name: str, column_name: str) -> bool:
    rows = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    return any(row[1] == column_name for row in rows)


def _add_column(conn, table_name: str, column_name: str, ddl: str):
    if not _column_exists(conn, table_name, column_name):
        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}"))


def migrate_add_customer_translation_fields():
    with engine.begin() as conn:
        # customer_service_items
        _add_column(conn, "customer_service_items", "content_zh", "TEXT")
        _add_column(conn, "customer_service_items", "title_zh", "TEXT")
        _add_column(conn, "customer_service_items", "translation_status", "VARCHAR(30) DEFAULT 'pending'")
        _add_column(conn, "customer_service_items", "translated_at", "DATETIME")
        _add_column(conn, "customer_service_items", "translation_error", "TEXT")
        _add_column(conn, "customer_service_items", "translation_source_hash", "VARCHAR(64)")

        # customer_service_messages
        _add_column(conn, "customer_service_messages", "message_text_zh", "TEXT")
        _add_column(conn, "customer_service_messages", "translation_status", "VARCHAR(30) DEFAULT 'pending'")
        _add_column(conn, "customer_service_messages", "translated_at", "DATETIME")
        _add_column(conn, "customer_service_messages", "translation_error", "TEXT")
        _add_column(conn, "customer_service_messages", "translation_source_hash", "VARCHAR(64)")

        print("[migration] add_customer_translation_fields 完成")
        return True


if __name__ == "__main__":
    success = migrate_add_customer_translation_fields()
    exit(0 if success else 1)