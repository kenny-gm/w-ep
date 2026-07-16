#!/usr/bin/env python3
"""Seed v2 fact tables from legacy tables.

Dry-run planning script. Actual writes must be added after validation queries
are approved.
"""

from __future__ import annotations


FACT_PLAN = {
    "fact_product_daily": ["orders", "order_items"],
    "fact_product_funnel_daily": ["ad_records where ad_type='product_analytics'"],
    "fact_ad_daily": ["ad_records where ad_type='advertising'"],
    "fact_ad_keyword_daily": ["ad_keyword_stats"],
    "fact_customer_signal_daily": ["customer_service_items", "customer_service_messages"],
    "fact_sync_health": ["sync_logs"],
}


def main() -> None:
    for target, sources in FACT_PLAN.items():
        print(f"{target}: {', '.join(sources)}")
    print("DRY RUN: no rows written.")


if __name__ == "__main__":
    main()

