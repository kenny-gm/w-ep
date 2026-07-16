#!/usr/bin/env python3
"""Sync WB API responses into the MySQL raw layer.

The script is conservative by default. Without --apply it only prints the plan.
The first executable batch is permission_probe: it calls a small set of
low-risk read-only endpoints and writes both success and permission failures to
the MySQL shadow raw tables.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any

import httpx
import pymysql
from pymysql.cursors import DictCursor


@dataclass(frozen=True)
class RawBatch:
    phase: str
    source_api: str
    endpoint: str
    target_table: str
    risk: str
    note: str


API_DOMAINS = {
    "common": "https://common-api.wildberries.ru",
    "content": "https://content-api.wildberries.ru",
    "marketplace": "https://marketplace-api.wildberries.ru",
    "analytics": "https://seller-analytics-api.wildberries.ru",
    "statistics": "https://statistics-api.wildberries.ru",
    "promotion": "https://advert-api.wildberries.ru",
    "finance": "https://finance-api.wildberries.ru",
    "feedbacks": "https://feedbacks-api.wildberries.ru",
    "buyer_chat": "https://buyer-chat-api.wildberries.ru",
    "returns": "https://returns-api.wildberries.ru",
}


BATCHES: list[RawBatch] = [
    RawBatch("permission_probe", "common", "/api/v1/seller-info", "wb_raw_api_responses", "low", "seller/token identity probe"),
    RawBatch("permission_probe", "content", "/content/v2/get/cards/list", "wb_raw_content_cards", "low", "first page only"),
    RawBatch("permission_probe", "promotion", "/api/advert/v2/adverts", "wb_raw_promotion_campaigns", "low", "campaign list probe"),
    RawBatch("permission_probe", "marketplace", "/api/v3/orders/new", "wb_raw_statistics_orders", "low", "new orders probe only"),
    RawBatch("permission_probe", "feedbacks", "/api/v1/questions", "wb_raw_customer_questions", "low", "take=1"),
    RawBatch("permission_probe", "feedbacks", "/api/v1/feedbacks", "wb_raw_customer_feedbacks", "low", "take=1"),
    RawBatch("permission_probe", "buyer_chat", "/api/v1/seller/chats", "wb_raw_customer_chats", "low", "limit=1"),
    RawBatch("permission_probe", "returns", "/api/v1/claims", "wb_raw_customer_returns", "low", "limit=1"),
    RawBatch("content", "content", "/content/v2/get/cards/list", "wb_raw_content_cards", "medium", "full cursor pagination"),
    RawBatch("content", "statistics", "/api/v1/supplier/stocks", "wb_raw_inventory_stocks", "medium", "product/barcode fallback"),
    RawBatch("content", "marketplace", "/api/v3/warehouses", "wb_raw_inventory_stocks", "low", "warehouse dictionary"),
    RawBatch("sales", "statistics", "/api/v1/supplier/orders", "wb_raw_statistics_orders", "medium", "official history window"),
    RawBatch("sales", "statistics", "/api/v1/supplier/sales", "wb_raw_statistics_sales", "medium", "sales/returns raw"),
    RawBatch("sales", "analytics", "/api/analytics/v3/sales-funnel/products/history", "wb_raw_analytics_product_funnel", "high", "low rate limit, nm/date windows"),
    RawBatch("ads", "promotion", "/api/advert/v2/adverts", "wb_raw_promotion_campaigns", "medium", "campaigns"),
    RawBatch("ads", "promotion", "/adv/v3/fullstats", "wb_raw_promotion_stats", "high", "50 advert ids per request"),
    RawBatch("ads", "promotion", "/adv/v1/normquery/stats", "wb_raw_promotion_keywords", "high", "keyword/search cluster stats"),
    RawBatch("customer", "feedbacks", "/api/v1/questions", "wb_raw_customer_questions", "medium", "paged"),
    RawBatch("customer", "feedbacks", "/api/v1/feedbacks", "wb_raw_customer_feedbacks", "medium", "paged"),
    RawBatch("customer", "buyer_chat", "/api/v1/seller/events", "wb_raw_customer_chats", "high", "cursor based, never reuse old cursor blindly"),
    RawBatch("customer", "returns", "/api/v1/claims", "wb_raw_customer_returns", "medium", "active/archive pages"),
    RawBatch("finance", "finance", "realization reports", "wb_raw_finance_realization_reports", "high", "financial source of truth"),
    RawBatch("finance", "finance", "documents", "wb_raw_finance_documents", "high", "documents/accounting"),
]


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


def load_wb_shops(sqlite_path: str) -> list[dict[str, Any]]:
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT id, name, platform, currency, is_active, api_token,
                   CASE WHEN api_token IS NULL OR api_token = '' THEN 0 ELSE length(api_token) END AS token_len
            FROM shops
            WHERE platform = 'wildberries' AND is_active = 1
            ORDER BY id
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def selected_batches(phase: str) -> list[RawBatch]:
    if phase == "all":
        return BATCHES
    return [batch for batch in BATCHES if batch.phase == phase]


def permission_probe_request(batch: RawBatch) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None]:
    if batch.source_api == "content":
        return (
            "POST",
            None,
            {
                "settings": {
                    "sort": {"ascending": False},
                    "filter": {"withPhoto": -1},
                    "cursor": {"limit": 1},
                }
            },
        )
    if batch.source_api == "feedbacks" and batch.endpoint in {"/api/v1/questions", "/api/v1/feedbacks"}:
        return "GET", {"take": 1, "skip": 0, "order": "dateDesc", "isAnswered": "false"}, None
    if batch.source_api == "buyer_chat":
        return "GET", {"limit": 1, "offset": 0}, None
    if batch.source_api == "returns":
        return "GET", {"limit": 1, "offset": 0, "is_archive": "false"}, None
    return "GET", None, None


def response_body(response: httpx.Response) -> Any:
    if not response.content:
        return {}
    try:
        return response.json()
    except json.JSONDecodeError:
        return {"text": response.text[:2000]}


def probe_endpoint(shop: dict[str, Any], batch: RawBatch, timeout: float) -> dict[str, Any]:
    method, params, json_data = permission_probe_request(batch)
    base_url = API_DOMAINS[batch.source_api]
    url = f"{base_url}{batch.endpoint}"
    headers = {"Authorization": shop["api_token"], "Content-Type": "application/json"}
    started_at = datetime.now(timezone.utc)

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.request(method, url, headers=headers, params=params, json=json_data)
        body = response_body(response)
        ok = 200 <= response.status_code < 300
        raw = {
            "ok": ok,
            "method": method,
            "url": url,
            "status_code": response.status_code,
            "request": {"params": params or {}, "json": json_data or {}},
            "response": body,
            "fetched_at": started_at.isoformat(),
        }
    except Exception as exc:
        raw = {
            "ok": False,
            "method": method,
            "url": url,
            "status_code": None,
            "request": {"params": params or {}, "json": json_data or {}},
            "error": type(exc).__name__,
            "message": str(exc)[:1000],
            "fetched_at": started_at.isoformat(),
        }

    return {
        "shop_id": shop["id"],
        "platform": "wildberries",
        "source_api": batch.source_api,
        "source_endpoint": batch.endpoint,
        "external_id": f"permission_probe:{batch.source_api}:{batch.endpoint}",
        "request_params_json": raw["request"],
        "raw_json": raw,
        "target_table": batch.target_table,
    }


def json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def insert_raw_rows(mysql_conn, rows: list[dict[str, Any]], sync_batch_id: str) -> None:
    sql = """
        INSERT INTO {table}
          (shop_id, platform, source_api, source_endpoint, external_id, sync_batch_id,
           request_params_json, raw_json, raw_hash)
        VALUES
          (%(shop_id)s, %(platform)s, %(source_api)s, %(source_endpoint)s, %(external_id)s,
           %(sync_batch_id)s, CAST(%(request_params_json)s AS JSON), CAST(%(raw_json)s AS JSON),
           %(raw_hash)s)
    """
    with mysql_conn.cursor() as cur:
        for row in rows:
            raw_json = json_dump(row["raw_json"])
            params_json = json_dump(row["request_params_json"])
            cur.execute(
                sql.format(table=row["target_table"]),
                {
                    "shop_id": row["shop_id"],
                    "platform": row["platform"],
                    "source_api": row["source_api"],
                    "source_endpoint": row["source_endpoint"],
                    "external_id": row["external_id"],
                    "sync_batch_id": sync_batch_id,
                    "request_params_json": params_json,
                    "raw_json": raw_json,
                    "raw_hash": hashlib.sha256(raw_json.encode("utf-8")).hexdigest(),
                },
            )
    mysql_conn.commit()


def count_rows_for_batch(mysql_conn, sync_batch_id: str) -> dict[str, int]:
    tables = sorted({batch.target_table for batch in BATCHES if batch.phase == "permission_probe"})
    counts: dict[str, int] = {}
    with mysql_conn.cursor() as cur:
        for table in tables:
            cur.execute(f"SELECT COUNT(*) AS count FROM {table} WHERE sync_batch_id = %s", (sync_batch_id,))
            counts[table] = int(cur.fetchone()["count"])
    return counts


def run_permission_probe(args: argparse.Namespace, shops: list[dict[str, Any]], batches: list[RawBatch]) -> None:
    if not args.mysql_user or not args.mysql_password:
        raise SystemExit("MYSQL_USER and MYSQL_PASSWORD are required with --apply")

    sync_batch_id = args.sync_batch_id or f"permission_probe_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    rows: list[dict[str, Any]] = []
    print(f"Running WB permission probe: batch={sync_batch_id}")
    for shop in shops:
        if not shop.get("api_token"):
            print(f"  shop {shop['id']} {shop['name']}: skipped, missing token")
            continue
        for batch in batches:
            row = probe_endpoint(shop, batch, args.timeout)
            rows.append(row)
            raw = row["raw_json"]
            status = raw.get("status_code")
            ok = "OK" if raw.get("ok") else "FAIL"
            print(f"  shop {shop['id']} {batch.source_api} {batch.endpoint}: {ok} status={status}")

    mysql_conn = mysql_connect(args)
    try:
        insert_raw_rows(mysql_conn, rows, sync_batch_id)
        print("MySQL raw rows written:")
        for table, count in count_rows_for_batch(mysql_conn, sync_batch_id).items():
            print(f"  {table}: {count}")
    finally:
        mysql_conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan WB raw API sync batches")
    parser.add_argument("--sqlite-path", default="/app/db/wb_erp.db")
    parser.add_argument(
        "--phase",
        choices=["permission_probe", "content", "sales", "ads", "customer", "finance", "all"],
        default="permission_probe",
    )
    parser.add_argument("--shop-id", type=int)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--sync-batch-id", default="")
    parser.add_argument("--mysql-host", default=os.getenv("MYSQL_HOST", "wb-erp-mysql"))
    parser.add_argument("--mysql-port", default=int(os.getenv("MYSQL_PORT", "3306")), type=int)
    parser.add_argument("--mysql-db", default=os.getenv("MYSQL_DATABASE", "wb_erp_shadow"))
    parser.add_argument("--mysql-user", default=os.getenv("MYSQL_USER", ""))
    parser.add_argument("--mysql-password", default=os.getenv("MYSQL_PASSWORD", ""))
    parser.add_argument("--apply", action="store_true", help="Call WB read-only endpoints and write MySQL shadow raw rows")
    args = parser.parse_args()

    shops = load_wb_shops(args.sqlite_path)
    if args.shop_id:
        shops = [shop for shop in shops if int(shop["id"]) == args.shop_id]

    batches = selected_batches(args.phase)
    print("WB raw API sync plan")
    print(f"  phase: {args.phase}")
    print(f"  shops: {len(shops)}")
    for shop in shops:
        print(f"    - {shop['id']} {shop['name']} currency={shop['currency']} token_len={shop['token_len']}")
    print(f"  days: {args.days}")
    print(f"  max_pages: {args.max_pages}")
    print(f"  planned endpoints: {len(batches)}")
    for batch in batches:
        print(f"    - [{batch.risk}] {batch.source_api} {batch.endpoint} -> {batch.target_table} ({batch.note})")

    if args.apply:
        if args.phase != "permission_probe":
            raise SystemExit("--apply is currently allowed only for --phase permission_probe")
        run_permission_probe(args, shops, batches)
        return
    print("dry-run only: no WB API calls, no MySQL writes")


if __name__ == "__main__":
    main()
