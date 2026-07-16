#!/usr/bin/env python3
"""Validation query catalog for SQLite -> MySQL migration.

This script prints required checks by default. It does not connect to MySQL
until validation implementation is filled in.
"""

from __future__ import annotations


VALIDATION_CHECKS = [
    "legacy row counts: shops/products/orders/order_items/ad_records/ad_keyword_stats/customer_service_*",
    "dim_product unique: shop_id + nm_id",
    "fact_ad_daily unique: shop_id + advert_id + nm_id + biz_date + payment_type + placements",
    "customer_service_messages message_dedup_key duplicates",
    "recent 7 day Dashboard sales/ad_cost/order_count parity",
    "CNY ad cost cutoff rule: before 2026-07-15 no double conversion, from 2026-07-15 convert by system rate",
    "system_settings.cny_to_rub overrides shops.exchange_rate in RUB views",
    "raw_json validity for raw layer JSON columns",
]


def main() -> None:
    for idx, check in enumerate(VALIDATION_CHECKS, start=1):
        print(f"{idx}. {check}")
    print("DRY RUN: validation execution not implemented yet.")


if __name__ == "__main__":
    main()

