#!/usr/bin/env python3
"""Backfill legacy operational tables from SQLite into MySQL.

The script is intentionally conservative:

- dry-run by default;
- never truncates or deletes target rows;
- skips non-empty MySQL tables unless --allow-non-empty is explicitly set;
- writes with INSERT IGNORE so existing primary/unique keys are preserved.

It is meant to cover the legacy tables still read by the current backend
routers during and after the MySQL cutover. The v2 dim/fact/view and WB raw
tables are handled by separate scripts and are excluded here.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from dataclasses import dataclass
from typing import Any

import pymysql
from pymysql.cursors import DictCursor


DEFAULT_LEGACY_TABLES = [
    "users",
    "shops",
    "products",
    "orders",
    "order_items",
    "ad_records",
    "ad_keyword_stats",
    "customer_service_items",
    "customer_service_messages",
    "customer_service_actions",
    "sync_logs",
    "sync_jobs",
    "system_settings",
    "metric_thresholds",
    "operation_logs",
    "ai_prompt_templates",
    "menu_items",
    "ui_settings",
]


EXCLUDED_PREFIXES = (
    "dim_",
    "fact_",
    "view_ops_",
    "wb_raw_",
    "migration_",
    "sqlite_",
)


ARCHIVE_OR_SKIP_TABLES = [
    "ad_records_new",
    "ai_configs",
    "ai_reports",
    "alerts",
    "alert_rules",
    "cs_lost_customer_service_actions",
    "cs_lost_customer_service_items",
    "cs_lost_customer_service_messages",
    "daily_stats",
    "product_sales_stats",
    "wayfair_catalog_products",
    "wayfair_inventory",
    "wayfair_order_items",
    "wayfair_orders",
    "wayfair_shipments",
    "wayfair_sync_logs",
]


@dataclass
class TablePlan:
    table: str
    source_count: int
    target_count: int | None
    common_columns: list[str]
    action: str
    detail: str


def mysql_connect(args: argparse.Namespace):
    return pymysql.connect(
        host=args.mysql_host,
        port=args.mysql_port,
        user=args.mysql_user,
        password=args.mysql_password,
        database=args.mysql_db,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )


def sqlite_tables(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {row["name"] for row in rows}


def sqlite_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [row["name"] for row in conn.execute(f'PRAGMA table_info("{table}")')]


def sqlite_count(conn: sqlite3.Connection, table: str) -> int:
    row = conn.execute(f'SELECT COUNT(*) AS count FROM "{table}"').fetchone()
    return int(row["count"] or 0)


def mysql_tables(conn) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT TABLE_NAME AS table_name
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            """
        )
        return {row["table_name"] for row in cur.fetchall()}


def mysql_columns(conn, table: str) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COLUMN_NAME AS column_name
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
            """,
            (table,),
        )
        return [row["column_name"] for row in cur.fetchall()]


def mysql_count(conn, table: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS count FROM `{table}`")
        return int(cur.fetchone()["count"] or 0)


def quote_ident(name: str) -> str:
    return "`" + name.replace("`", "``") + "`"


def parse_table_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def default_tables(source_tables: set[str], target_tables: set[str]) -> list[str]:
    tables = [table for table in DEFAULT_LEGACY_TABLES if table in source_tables and table in target_tables]
    return [table for table in tables if not table.startswith(EXCLUDED_PREFIXES)]


def build_plan(sqlite_conn: sqlite3.Connection, mysql_conn, args: argparse.Namespace) -> list[TablePlan]:
    source_tables = sqlite_tables(sqlite_conn)
    target_tables = mysql_tables(mysql_conn)
    requested_tables = parse_table_list(args.tables) if args.tables else default_tables(source_tables, target_tables)

    plans: list[TablePlan] = []
    for table in requested_tables:
        if table.startswith(EXCLUDED_PREFIXES):
            plans.append(TablePlan(table, 0, None, [], "skip", "excluded v2/raw/internal table"))
            continue
        if table not in source_tables:
            plans.append(TablePlan(table, 0, None, [], "skip", "missing in SQLite source"))
            continue
        if table not in target_tables:
            plans.append(TablePlan(table, sqlite_count(sqlite_conn, table), None, [], "skip", "missing in MySQL target"))
            continue

        source_columns = sqlite_columns(sqlite_conn, table)
        target_columns = mysql_columns(mysql_conn, table)
        target_column_set = set(target_columns)
        common_columns = [column for column in source_columns if column in target_column_set]
        source_count = sqlite_count(sqlite_conn, table)
        target_count = mysql_count(mysql_conn, table)

        if source_count == 0:
            action = "skip"
            detail = "source table is empty"
        elif not common_columns:
            action = "skip"
            detail = "no shared columns"
        elif target_count > 0 and not args.allow_non_empty:
            action = "skip"
            detail = "target table is non-empty; pass --allow-non-empty for INSERT IGNORE backfill"
        else:
            action = "copy"
            detail = "ready"

        plans.append(TablePlan(table, source_count, target_count, common_columns, action, detail))

    return plans


def batched_rows(conn: sqlite3.Connection, table: str, columns: list[str], batch_size: int):
    column_sql = ", ".join(f'"{column}"' for column in columns)
    sql = f'SELECT {column_sql} FROM "{table}"'
    cursor = conn.execute(sql)
    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        yield [tuple(row[column] for column in columns) for row in rows]


def copy_table(sqlite_conn: sqlite3.Connection, mysql_conn, plan: TablePlan, batch_size: int) -> int:
    columns_sql = ", ".join(quote_ident(column) for column in plan.common_columns)
    placeholders = ", ".join(["%s"] * len(plan.common_columns))
    insert_sql = f"INSERT IGNORE INTO {quote_ident(plan.table)} ({columns_sql}) VALUES ({placeholders})"

    inserted_total = 0
    with mysql_conn.cursor() as cur:
        for batch in batched_rows(sqlite_conn, plan.table, plan.common_columns, batch_size):
            inserted_total += cur.executemany(insert_sql, batch)
    return inserted_total


def print_plan(plans: list[TablePlan]) -> None:
    print("Legacy table backfill plan:")
    for plan in plans:
        target = "-" if plan.target_count is None else str(plan.target_count)
        print(
            f"  {plan.table}: source={plan.source_count}, target={target}, "
            f"columns={len(plan.common_columns)}, action={plan.action}, detail={plan.detail}"
        )
    print("Archive/skip reference:", ", ".join(ARCHIVE_OR_SKIP_TABLES))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite-path", default="/app/db/wb_erp.db")
    parser.add_argument("--mysql-host", default=os.getenv("MYSQL_HOST", "wb-erp-mysql"))
    parser.add_argument("--mysql-port", default=int(os.getenv("MYSQL_PORT", "3306")), type=int)
    parser.add_argument("--mysql-db", default=os.getenv("MYSQL_DATABASE", "wb_erp_shadow"))
    parser.add_argument("--mysql-user", default=os.getenv("MYSQL_USER", ""))
    parser.add_argument("--mysql-password", default=os.getenv("MYSQL_PASSWORD", ""))
    parser.add_argument("--tables", default="", help="Comma-separated legacy table allowlist")
    parser.add_argument("--batch-size", default=500, type=int)
    parser.add_argument("--allow-non-empty", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Accepted for compatibility; dry-run is the default")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not args.mysql_user or not args.mysql_password:
        raise SystemExit("MYSQL_USER and MYSQL_PASSWORD are required")

    sqlite_conn = sqlite3.connect(args.sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    mysql_conn = mysql_connect(args)

    try:
        plans = build_plan(sqlite_conn, mysql_conn, args)
        print_plan(plans)

        copy_plans = [plan for plan in plans if plan.action == "copy"]
        if not args.apply:
            print("DRY RUN: no rows written.")
            return

        if not copy_plans:
            print("APPLY: no eligible tables to copy.")
            return

        print("APPLY: copying eligible legacy tables with INSERT IGNORE.")
        for plan in copy_plans:
            inserted = copy_table(sqlite_conn, mysql_conn, plan, args.batch_size)
            print(f"  {plan.table}: inserted={inserted}, source={plan.source_count}")
        mysql_conn.commit()
    except Exception:
        mysql_conn.rollback()
        raise
    finally:
        mysql_conn.close()
        sqlite_conn.close()


if __name__ == "__main__":
    main()
