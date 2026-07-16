#!/usr/bin/env python3
"""Plan WB API raw-layer sync batches.

This script is intentionally dry-run only for now. It does not call WB API and
does not write MySQL. The next implementation step will add the permission
probe batch behind an explicit --apply flag.
"""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RawBatch:
    phase: str
    source_api: str
    endpoint: str
    target_table: str
    risk: str
    note: str


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


def load_wb_shops(sqlite_path: str) -> list[dict[str, Any]]:
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT id, name, platform, currency, is_active,
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
    parser.add_argument("--apply", action="store_true", help="Reserved for the next implementation step")
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
        raise SystemExit("--apply is not implemented yet; implement permission_probe first to avoid accidental full WB pulls")
    print("dry-run only: no WB API calls, no MySQL writes")


if __name__ == "__main__":
    main()
