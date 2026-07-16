#!/usr/bin/env python3
"""Legacy table migration skeleton.

This script intentionally does not implement data writes yet. The next step is
to fill table-by-table ETL after the MySQL shadow schema is approved.
"""

from __future__ import annotations

import argparse


LEGACY_TABLES = [
    "shops",
    "users",
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


ARCHIVE_OR_SKIP_TABLES = [
    "ad_records_new",
    "cs_lost_customer_service_items",
    "cs_lost_customer_service_messages",
    "cs_lost_customer_service_actions",
    "wayfair_catalog_products",
    "wayfair_inventory",
    "wayfair_order_items",
    "wayfair_orders",
    "wayfair_shipments",
    "wayfair_sync_logs",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"{mode}: legacy migration plan")
    print("Migrate:", ", ".join(LEGACY_TABLES))
    print("Archive/skip:", ", ".join(ARCHIVE_OR_SKIP_TABLES))
    if not args.apply:
        print("No rows copied. Implement table ETL after shadow MySQL is approved.")


if __name__ == "__main__":
    main()

