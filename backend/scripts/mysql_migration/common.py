"""Shared helpers for MySQL v2 migration scripts.

The helpers are intentionally conservative: scripts are dry-run by default and
require explicit flags before writing to a target database.
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
except ModuleNotFoundError:
    create_engine = None
    text = None
    Engine = Any


def build_engine(url: str) -> Engine:
    if create_engine is None:
        raise RuntimeError("SQLAlchemy is required for database connections")
    connect_args: dict[str, Any] = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False, "timeout": 30}
    return create_engine(url, connect_args=connect_args, pool_pre_ping=True)


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--sqlite-url", default="sqlite:////app/db/wb_erp.db")
    parser.add_argument("--mysql-url", default="")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--apply", action="store_true", help="Allow writes to target database")


def ensure_apply(args: argparse.Namespace) -> None:
    if not args.apply:
        raise SystemExit("Refusing to write without --apply")


def parse_json_value(value: Any, default: Any = None) -> Any:
    if value in (None, ""):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default


def to_decimal(value: Any, default: str = "0") -> Decimal:
    if value in (None, ""):
        return Decimal(default)
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def to_bool_int(value: Any) -> int:
    if isinstance(value, bool):
        return 1 if value else 0
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return 1 if value else 0
    return 1 if str(value).strip().lower() in {"1", "true", "yes", "on"} else 0


def to_date_string(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.date().isoformat()
    text_value = str(value)
    return text_value[:10] if len(text_value) >= 10 else text_value


def load_sql(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def sqlite_table_names(engine: Engine) -> list[str]:
    if text is None:
        raise RuntimeError("SQLAlchemy is required for SQLite schema scanning")
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ).fetchall()
    return [row[0] for row in rows]
