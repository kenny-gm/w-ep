#!/usr/bin/env python3
"""Seed v2 dimension tables from legacy tables.

Dry-run planning script. Actual writes must be added table by table after
shadow MySQL is available.
"""

from __future__ import annotations


DIMENSION_PLAN = {
    "dim_shop": ["shops"],
    "dim_owner": ["users", "products.owner"],
    "dim_product": ["products"],
    "dim_product_group": ["products.custom_name"],
    "dim_product_group_member": ["products.custom_name", "products.shop_id", "products.nm_id"],
    "dim_ad_campaign": ["ad_records.advert_id", "ad_keyword_stats.advert_id"],
    "dim_currency_rate": ["system_settings.cny_to_rub", "shops.currency"],
}


def main() -> None:
    for target, sources in DIMENSION_PLAN.items():
        print(f"{target}: {', '.join(sources)}")
    print("DRY RUN: no rows written.")


if __name__ == "__main__":
    main()

