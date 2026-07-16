#!/usr/bin/env python3
"""Create MySQL v2 schema from docs/mysql-v2-schema.sql.

Default mode is dry-run. Use --apply and --mysql-url only after explicit
approval and after MySQL shadow database exists.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from common import build_engine, ensure_apply, load_sql


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ddl", default="docs/mysql-v2-schema.sql")
    parser.add_argument("--mysql-url", default="")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    ddl_path = Path(args.ddl)
    sql = load_sql(ddl_path)

    if not args.apply:
        print(f"DRY RUN: loaded {ddl_path} ({len(sql)} bytes). No SQL executed.")
        return

    ensure_apply(args)
    if not args.mysql_url:
        raise SystemExit("--mysql-url is required with --apply")

    from sqlalchemy import text

    engine = build_engine(args.mysql_url)
    statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
    print(f"Applied {len(statements)} SQL statements from {ddl_path}")


if __name__ == "__main__":
    main()
