#!/bin/bash

LOG_FILE="/opt/wb-erp/logs/healthcheck.log"

# 检查服务状态
if ! curl -s -f http://localhost/health > /dev/null 2>&1; then
    echo "$(date): ❌ 服务异常，重启中..." >> $LOG_FILE
    cd /opt/wb-erp && docker-compose restart
    sleep 10
    if curl -s -f http://localhost/health > /dev/null 2>&1; then
        echo "$(date): ✅ 服务已恢复" >> $LOG_FILE
    else
        echo "$(date): ❌ 重启失败" >> $LOG_FILE
    fi
fi
