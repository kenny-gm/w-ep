#!/usr/bin/env python3
"""Scan SQLite schema and print a JSON summary.

This script is read-only. It is safe to run against the current SQLite volume.
"""

from __future__ import annotations

import argparse
import json

from sqlalchemy import text

from common import build_engine, sqlite_table_names


def scan(sqlite_url: str) -> dict:
    engine = build_engine(sqlite_url)
    result: dict[str, object] = {"tables": []}
    with engine.connect() as conn:
        for table_name in sqlite_table_names(engine):
            row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            columns = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
            indexes = conn.execute(text(f"PRAGMA index_list({table_name})")).fetchall()
            result["tables"].append(
                {
                    "name": table_name,
                    "row_count": row_count,
                    "columns": [
                        {
                            "name": col[1],
                            "type": col[2],
                            "not_null": bool(col[3]),
                            "default": col[4],
                            "primary_key": bool(col[5]),
                        }
                        for col in columns
                    ],
                    "indexes": [
                        {"name": idx[1], "unique": bool(idx[2])}
                        for idx in indexes
                    ],
                }
            )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite-url", default="sqlite:////app/db/wb_erp.db")
    args = parser.parse_args()
    print(json.dumps(scan(args.sqlite_url), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

