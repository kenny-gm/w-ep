#!/bin/bash
LOG=/opt/wb-erp/logs/sync.log
INTERNAL_KEY="wb-erp-internal-sync-key-2026"

echo "$(date): 开始同步" >> $LOG

# 动态获取所有活跃店铺ID
shop_ids=$(docker exec wb-erp-backend python3 /app/backend/get_shop_ids.py 2>&1 | grep -oE '[0-9]+' | paste -sd ' ' | tr -d '\n')

for shop_id in $shop_ids; do
    echo "$(date): 同步店铺 $shop_id..." >> $LOG
    RESULT=$(curl -s -X POST "http://localhost:8000/api/shops/internal-sync/${shop_id}/?api_key=${INTERNAL_KEY}&sync_type=all")
    echo "$RESULT" >> $LOG
done

echo "$(date): 同步完成" >> $LOG
