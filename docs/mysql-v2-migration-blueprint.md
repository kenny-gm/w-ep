# MySQL v2 Migration Blueprint

更新时间：2026-07-16

目标：借 MySQL 迁移机会，把现有 SQLite 旧结构升级为面向 WB API 全字段、运营分析、AI 建议、站内信和任务系统的 v2 数据结构。

本文件是迁移蓝图和兼容性扫描报告，不执行数据库迁移，不修改生产数据。

## 1. 扫描结论

当前建议：现有业务系统不推倒重写，但数据库层不要做 SQLite 表结构 1:1 搬迁。应采用“旧表兼容 + v2 新结构 + 影子库双跑 + 分模块切换”的路线。

已确认的现场事实：

- 后端默认数据库仍为 `sqlite:////app/db/wb_erp.db`。
- `docker-compose.yml` 当前只有 `backend` 和 `frontend`，没有 MySQL 服务。
- 后端启动时在 `main.py` 中直接执行 `Base.metadata.create_all(bind=engine)`。
- 后端启动时会执行多段手写 migration。
- 当前没有 Alembic 标准迁移体系。
- `products.nm_id` 当前为全局唯一索引，不适合多店铺同 nmId。
- `ad_records` 同时存放广告统计和商品漏斗数据，依赖 `ad_type=advertising/product_analytics` 区分。
- 生产 SQLite 当前有 37 张表，包含历史残留表和空表。

本轮只读扫描命令：

```bash
git -C /opt/wb-erp status --short
rg --files /opt/wb-erp/backend
rg -n "sqlite_master|PRAGMA|INSERT OR REPLACE|ON CONFLICT|json_extract|func\\.date|DateTime|Boolean|JSON|create_all|ALTER TABLE|CREATE INDEX|DROP INDEX|migrations|DATABASE_URL|sqlite" /opt/wb-erp/backend /opt/wb-erp/docker-compose.yml
docker exec -i wb-erp-backend python - <<'PY'
from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    tables = [r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")).fetchall()]
    print("TABLE_COUNT", len(tables))
    for t in tables:
        cnt = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        cols = conn.execute(text(f"PRAGMA table_info({t})")).fetchall()
        idx = conn.execute(text(f"PRAGMA index_list({t})")).fetchall()
        print(t, cnt, cols, idx)
PY
```

## 2. 当前生产库表现状

只读扫描结果：当前 SQLite 有 37 张业务表。

| 表 | 行数 | 迁移建议 |
| --- | ---: | --- |
| shops | 5 | 保留旧表兼容，同时映射到 `dim_shop` |
| products | 169 | 保留旧表兼容，同时拆到 `dim_product` / `dim_product_group` |
| orders | 2065 | 保留旧表兼容，但不能作为完整 WB 原始订单 |
| order_items | 907 | 保留旧表兼容，后续由 Statistics / Finance 重建 |
| ad_records | 30135 | 保留旧表兼容，v2 拆为广告事实和商品漏斗事实 |
| ad_keyword_stats | 181906 | 保留旧表兼容，v2 映射到 `fact_ad_keyword_daily` |
| customer_service_items | 4616 | 保留，可作为客服统一工单 v1，后续扩展 raw 层 |
| customer_service_messages | 19671 | 保留，可作为客服消息事实 |
| customer_service_actions | 26 | 保留，后续扩展操作审计 |
| sync_logs | 28042 | 保留，后续映射到 `fact_sync_health` |
| sync_jobs | 7 | 保留，后续统一任务执行状态 |
| system_settings | 16 | 保留 |
| users | 8 | 保留，并映射到 `dim_owner` / 权限体系 |
| menu_items | 7 | 保留 |
| ui_settings | 1 | 保留 |
| metric_thresholds | 3 | 保留，用于运营预警阈值 |
| operation_logs | 421 | 保留，后续可接入任务复盘 |
| ai_prompt_templates | 9 | 保留 |
| ai_configs / ai_reports / alert_rules / alerts | 0 | 历史空表，迁移前确认是否保留 |
| inventory_records / inventory_snapshots / metric_histories | 0 | 当前不是生产主链路，v2 重新设计 |
| ad_records_new | 0 | 历史残留表，迁移前标记为可清理候选 |
| cs_lost_customer_service_* | 4 / 7065 / 423 | 历史恢复残留，不直接进入 v2 主链路 |
| wayfair_* | 0 | 与 WB v2 迁移无关，可暂不迁入 v2 |

## 3. MySQL 兼容性风险分级

### P0：迁移前必须处理

1. 启动时手写 migration 混杂

证据：

- `backend/app/main.py` 在应用启动时直接执行多段 migration。
- `Base.metadata.create_all(bind=engine)` 也在启动时执行。
- 多个 migration 使用 SQLite 专用语句。

风险：

- MySQL 切换后，启动过程中可能执行不兼容 DDL。
- migration 失败会直接影响后端启动。
- 没有版本表，无法可靠知道生产库处于哪个 schema 版本。

处理建议：

- MySQL 迁移前建立 `schema_migrations` 或 Alembic。
- 将启动时 migration 从 `main.py` 移出，改为显式迁移命令。
- 老 SQLite migration 保留为 legacy，只对 SQLite 运行。

2. SQLite 专用迁移语句

证据：

- `sqlite_master`
- `PRAGMA table_info`
- `PRAGMA index_list`
- `PRAGMA index_xinfo`
- `sqlite3` 原生连接
- `DROP INDEX IF EXISTS`
- `CREATE INDEX IF NOT EXISTS`

涉及文件：

```text
backend/app/init_db.py
backend/migrations/add_ai_prompt_templates.py
backend/migrations/add_buyer_key_column.py
backend/migrations/add_customer_service_internal_note.py
backend/migrations/add_customer_translation_fields.py
backend/migrations/add_sync_lock.py
backend/migrations/fix_ad_records_dedup_index.py
backend/migrations/fix_customer_service_items_columns.py
backend/migrations/fix_customer_service_message_unique.py
backend/migrations/msg_dedup_migration.py
backend/migrations/optimize_customer_reply_prompt.py
```

处理建议：

- 所有迁移函数必须按 `engine.dialect.name` 分支。
- MySQL 下用 `information_schema` 查询表/列/索引。
- `msg_dedup_migration.py` 当前直接 `import sqlite3`，不能在 MySQL 路径运行。

3. `products.nm_id` 全局唯一

证据：

- `Product.nm_id = Column(String(50), unique=True, index=True, nullable=False)`。
- 生产索引：`ix_products_nm_id UNIQUE`。
- 同步代码中存在“nm_id 已在其他店铺存在则跳过”的逻辑。

风险：

- 多店铺同 nmId 或未来多平台同商品 ID 会冲突。
- 产品组聚合被迫依赖 `custom_name`，底层缺少稳定多店铺映射。

处理建议：

- legacy 旧表暂保留。
- v2 商品维表使用唯一键：`UNIQUE(shop_id, nm_id)`。
- 新增 `dim_product_group` 与 `dim_product_group_member` 承接运营产品组。

4. `ad_records` 混合广告和商品漏斗

证据：

- `ad_records.ad_type` 当前用于区分 `advertising` 和 `product_analytics`。
- Dashboard / 产品明细 / 广告分析均依赖该表。
- 生产表 `record_date` 实际为 `TEXT`，模型定义为 `DateTime`。

风险：

- 广告费用、商品漏斗、销售金额口径容易混淆。
- MySQL DateTime 比 SQLite 更严格，`func.date(record_date)` 相关逻辑需重点验证。

处理建议：

- legacy 旧表继续支撑现有页面。
- v2 拆分为：
  - `fact_product_funnel_daily`
  - `fact_ad_daily`
  - `fact_ad_keyword_daily`
  - `dim_ad_campaign`

5. 生产库存在历史残留表

证据：

- `ad_records_new` 行数 0。
- `cs_lost_customer_service_items/messages/actions` 是历史恢复残留。
- `wayfair_*` 全部 0 行。

风险：

- 1:1 dump 会把无关历史表带入 MySQL，污染新结构。

处理建议：

- legacy 迁移清单必须分为“保留、归档、不迁移”三类。
- `cs_lost_*` 只归档，不进入主业务事实层。

### P1：迁移前建议处理

1. JSON 字段类型不统一

证据：

- 模型里 `users.allowed_menus/allowed_owners/permissions/allowed_shops` 是 SQLAlchemy `JSON`。
- `shops.platform_config` 模型是 `JSON`，生产库实际是 `TEXT`。
- 客服和动作表大量 `raw_json/request_json/response_json` 为 `TEXT`。

建议：

- MySQL v2 raw 层使用 `JSON` 类型存 `raw_json`。
- legacy 兼容层可先用 `LONGTEXT`，避免旧代码解析失败。
- ETL 脚本对 JSON 字段做合法性校验，不合法时写入文本并记录异常。

2. Boolean 类型需要规范化

证据：

- SQLite 里布尔值实际为 `INTEGER/NUM/BOOLEAN` 混合。
- MySQL 应统一为 `TINYINT(1)` 或 SQLAlchemy Boolean。

建议：

- ETL 中将 `None/0/1/true/false` 显式转换。
- 所有布尔字段设置默认值。

3. Date / DateTime / Text 混用

证据：

- `ad_records.record_date` 生产表为 `TEXT`，模型是 `DateTime`。
- `metric_histories.date` 生产表为 `VARCHAR(10)`，模型是 `DateTime`。
- `operation_logs.log_date` 生产表为 `VARCHAR(10)`，模型是 `DateTime`。

建议：

- v2 每日事实表统一使用 `biz_date DATE`。
- 事件时间统一使用 `created_at DATETIME` / `external_created_at DATETIME`。
- ETL 转换失败必须写入迁移错误表。

4. 原始 WB API 响应保留不足

证据：

- 客服表已有 `raw_json`，方向正确。
- 商品、广告、订单等核心链路缺少统一 raw 层。

建议：

- 先补 raw 层，再从 raw 生成 fact。
- 后续字段扩展优先从 raw 重算，避免重新拉历史。

### P2：迁移后优化

- 引入 Alembic 版本化迁移。
- 将前端页面逐步切换到 `view_ops_*`。
- 将历史空表和归档表从生产主库迁到 archive。
- 增加 `fact_sync_health` 监控每个 API 数据域的同步质量。
- 统一 SQLAlchemy 模型和真实库字段，消除旧字段名差异。

## 4. MySQL v2 目标结构

### 4.1 legacy 兼容层

第一阶段 MySQL 中保留当前业务表名，保证旧页面可继续运行：

```text
shops
users
products
orders
order_items
ad_records
ad_keyword_stats
customer_service_items
customer_service_messages
customer_service_actions
sync_logs
sync_jobs
system_settings
metric_thresholds
operation_logs
ai_prompt_templates
menu_items
ui_settings
```

以下表仅归档或暂不迁入主链路：

```text
ad_records_new
cs_lost_customer_service_items
cs_lost_customer_service_messages
cs_lost_customer_service_actions
wayfair_*
ai_configs
ai_reports
alert_rules
alerts
```

### 4.2 raw 原始层

Raw 层目标：保存 WB API 原始响应，任何字段缺失都能回溯。

通用字段：

```text
id BIGINT PRIMARY KEY AUTO_INCREMENT
shop_id BIGINT NOT NULL
platform VARCHAR(30) NOT NULL DEFAULT 'wildberries'
source_api VARCHAR(50) NOT NULL
source_endpoint VARCHAR(200) NOT NULL
external_id VARCHAR(200)
sync_batch_id VARCHAR(100) NOT NULL
external_created_at DATETIME NULL
external_updated_at DATETIME NULL
raw_json JSON NOT NULL
raw_hash CHAR(64) NULL
fetched_at DATETIME NOT NULL
created_at DATETIME NOT NULL
updated_at DATETIME NOT NULL
```

建议表：

```text
wb_raw_api_responses
wb_raw_content_cards
wb_raw_prices
wb_raw_discounts
wb_raw_inventory_stocks
wb_raw_statistics_orders
wb_raw_statistics_sales
wb_raw_analytics_product_funnel
wb_raw_analytics_search_terms
wb_raw_promotion_campaigns
wb_raw_promotion_stats
wb_raw_promotion_keywords
wb_raw_customer_questions
wb_raw_customer_feedbacks
wb_raw_customer_chats
wb_raw_customer_returns
wb_raw_finance_realization_reports
wb_raw_finance_documents
```

### 4.3 dimensions 维表层

```text
dim_shop
dim_owner
dim_product
dim_product_variant
dim_product_group
dim_product_group_member
dim_ad_campaign
dim_warehouse
dim_currency_rate
dim_api_token_permission
```

关键唯一键：

```text
dim_product: UNIQUE(shop_id, nm_id)
dim_product_variant: UNIQUE(shop_id, nm_id, barcode)
dim_product_group_member: UNIQUE(product_group_id, shop_id, nm_id)
dim_ad_campaign: UNIQUE(shop_id, advert_id)
dim_warehouse: UNIQUE(shop_id, warehouse_external_id)
dim_currency_rate: UNIQUE(currency_from, currency_to, effective_date)
```

### 4.4 facts 事实层

```text
fact_product_daily
fact_product_funnel_daily
fact_order_daily
fact_sales_daily
fact_ad_daily
fact_ad_keyword_daily
fact_inventory_daily
fact_customer_signal_daily
fact_finance_daily
fact_sync_health
```

关键口径：

- 商品漏斗来自 Analytics。
- 运营订单来自 Statistics / Marketplace。
- 广告费用来自 Promotion。
- 财务利润来自 Finance realization report。
- 客服信号来自 Questions / Feedbacks / Chat / Returns。
- CNY/RUB 原币种保留，统一卢布只在 view 或 fact 派生字段中生成。

### 4.5 views 展示层

前端不直接查 raw，逐步改读稳定 view：

```text
view_ops_overview
view_ops_dashboard_trend
view_ops_product_daily
view_ops_product_matrix
view_ops_ad_efficiency
view_ops_customer_signals
view_ops_finance_profit
view_ops_owner_tasks
```

### 4.6 ops 工作流层

用于站内信、站内任务、AI 建议：

```text
internal_messages
ops_tasks
ops_task_comments
ops_task_actions
ops_task_checklists
ops_task_links
ops_ai_suggestions
ops_task_templates
ops_task_review_snapshots
```

任务和数据链路：

```text
view_ops_* 异常
  -> ops_ai_suggestions
  -> internal_messages
  -> ops_tasks
  -> 产品负责人处理
  -> 主管验收
  -> ops_task_review_snapshots
```

## 5. 旧表到 v2 映射

| 当前表 | v2 目标 | 迁移方式 |
| --- | --- | --- |
| shops | `dim_shop` | 直接映射，补充 seller/token 权限字段 |
| users | `dim_owner` + 权限表 | owner 维度从 `Product.owner` 和 `User.allowed_owners` 生成 |
| products | `dim_product` / `dim_product_group` | 保留旧产品 ID，新增 `shop_id + nm_id` 业务唯一 |
| orders | `fact_order_daily` legacy seed | 仅作为旧运营订单参考，不当作完整 WB 原始订单 |
| order_items | `fact_order_line` legacy seed | 等 Statistics / Finance 接入后重建 |
| ad_records(ad_type=product_analytics) | `fact_product_funnel_daily` | 按 `product_id/shop_id/record_date` 转换 |
| ad_records(ad_type=advertising) | `fact_ad_daily` | 按 `shop_id/product_id/advert_id/record_date` 转换 |
| ad_keyword_stats | `fact_ad_keyword_daily` | 按 `shop_id/product_id/advert_id/nm_id/date/keyword` 转换 |
| customer_service_items | `fact_customer_signal_daily` + `wb_raw_customer_*` | 保留工单主表，后续按渠道拆 raw |
| customer_service_messages | 客服消息事实 | 保留并补 raw 链接 |
| customer_service_actions | `ops_task_actions` / 客服动作审计 | 保留并扩展 |
| sync_logs | `fact_sync_health` | 生成同步健康状态 |
| operation_logs | `ops_task_review_snapshots` seed | 后续和任务复盘关联 |
| metric_thresholds | 预警规则 | 保留 |

## 6. MySQL DDL 草案

说明：以下是草案，正式执行前需要生成完整 migration 文件并在影子库验证。

```sql
CREATE TABLE dim_product (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  legacy_product_id BIGINT NULL,
  shop_id BIGINT NOT NULL,
  nm_id VARCHAR(50) NOT NULL,
  imt_id VARCHAR(50) NULL,
  supplier_article VARCHAR(120) NULL,
  sku VARCHAR(120) NULL,
  name VARCHAR(500) NULL,
  custom_name VARCHAR(500) NULL,
  owner VARCHAR(100) NULL,
  subject_id VARCHAR(50) NULL,
  subject_name VARCHAR(200) NULL,
  brand VARCHAR(200) NULL,
  raw_card_id BIGINT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  UNIQUE KEY uq_dim_product_shop_nm (shop_id, nm_id),
  KEY ix_dim_product_owner (owner),
  KEY ix_dim_product_custom_name (custom_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE dim_product_group (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  group_name VARCHAR(500) NOT NULL,
  owner VARCHAR(100) NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  UNIQUE KEY uq_dim_product_group_name (group_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE fact_product_funnel_daily (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  nm_id VARCHAR(50) NOT NULL,
  biz_date DATE NOT NULL,
  impressions INT NOT NULL DEFAULT 0,
  visitors INT NOT NULL DEFAULT 0,
  clicks INT NOT NULL DEFAULT 0,
  cart_count INT NOT NULL DEFAULT 0,
  order_count INT NOT NULL DEFAULT 0,
  sales_amount DECIMAL(18,2) NOT NULL DEFAULT 0,
  currency VARCHAR(10) NOT NULL DEFAULT 'RUB',
  sales_amount_rub DECIMAL(18,2) NOT NULL DEFAULT 0,
  source_raw_id BIGINT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  UNIQUE KEY uq_product_funnel_day (shop_id, nm_id, biz_date),
  KEY ix_product_funnel_product_date (product_id, biz_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE fact_ad_daily (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  product_id BIGINT NULL,
  nm_id VARCHAR(50) NULL,
  advert_id BIGINT NOT NULL,
  biz_date DATE NOT NULL,
  ad_type VARCHAR(50) NOT NULL,
  payment_type VARCHAR(30) NULL,
  placements VARCHAR(80) NULL,
  impressions INT NOT NULL DEFAULT 0,
  clicks INT NOT NULL DEFAULT 0,
  visitors INT NOT NULL DEFAULT 0,
  cart_count INT NOT NULL DEFAULT 0,
  order_count INT NOT NULL DEFAULT 0,
  ad_cost DECIMAL(18,2) NOT NULL DEFAULT 0,
  ad_cost_currency VARCHAR(10) NOT NULL DEFAULT 'RUB',
  ad_cost_rub DECIMAL(18,2) NOT NULL DEFAULT 0,
  sales_amount DECIMAL(18,2) NOT NULL DEFAULT 0,
  sales_amount_rub DECIMAL(18,2) NOT NULL DEFAULT 0,
  source_raw_id BIGINT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  UNIQUE KEY uq_ad_daily (shop_id, advert_id, nm_id, biz_date, payment_type, placements),
  KEY ix_ad_daily_product_date (product_id, biz_date),
  KEY ix_ad_daily_shop_date (shop_id, biz_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE ops_tasks (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(300) NOT NULL,
  task_type VARCHAR(50) NOT NULL,
  source_type VARCHAR(30) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'pending',
  priority VARCHAR(20) NOT NULL DEFAULT 'normal',
  assignee_owner VARCHAR(100) NULL,
  assignee_user_id BIGINT NULL,
  created_by BIGINT NULL,
  reviewer_id BIGINT NULL,
  due_at DATETIME NULL,
  progress INT NOT NULL DEFAULT 0,
  ai_summary TEXT NULL,
  ai_reason TEXT NULL,
  ai_suggested_actions JSON NULL,
  metrics_snapshot_json JSON NULL,
  result_note TEXT NULL,
  completed_at DATETIME NULL,
  reviewed_at DATETIME NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  KEY ix_ops_tasks_assignee_status (assignee_owner, status),
  KEY ix_ops_tasks_due_status (due_at, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 7. ETL 迁移脚本设计

迁移脚本建议放在：

```text
backend/scripts/mysql_migration/
  01_scan_sqlite_schema.py
  02_create_mysql_v2_schema.py
  03_migrate_legacy_tables.py
  04_seed_v2_dimensions.py
  05_seed_v2_facts.py
  06_validate_migration.py
```

执行原则：

- 只读 SQLite，写 MySQL。
- 每批迁移写入 `migration_batches`。
- 每张表按批处理，不一次性读入大表。
- 每条失败记录写入 `migration_errors`。
- 对金额使用 Decimal，避免 float 二次误差扩大。
- JSON 字段先校验合法性，不合法则写入错误表或转为 LONGTEXT。

建议迁移批次表：

```sql
CREATE TABLE migration_batches (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  batch_key VARCHAR(100) NOT NULL,
  source_db VARCHAR(200) NOT NULL,
  target_db VARCHAR(200) NOT NULL,
  status VARCHAR(30) NOT NULL,
  started_at DATETIME NOT NULL,
  finished_at DATETIME NULL,
  result_json JSON NULL,
  UNIQUE KEY uq_migration_batch_key (batch_key)
);
```

## 8. 校验清单

### 8.1 行数校验

```sql
-- SQLite 与 MySQL legacy 表行数必须一致
shops
products
orders
order_items
ad_records
ad_keyword_stats
customer_service_items
customer_service_messages
customer_service_actions
sync_logs
system_settings
users
```

### 8.2 唯一键校验

```sql
-- 产品 v2 唯一键
SELECT shop_id, nm_id, COUNT(*)
FROM dim_product
GROUP BY shop_id, nm_id
HAVING COUNT(*) > 1;

-- 广告事实唯一键
SELECT shop_id, advert_id, nm_id, biz_date, payment_type, placements, COUNT(*)
FROM fact_ad_daily
GROUP BY shop_id, advert_id, nm_id, biz_date, payment_type, placements
HAVING COUNT(*) > 1;

-- 客服消息去重
SELECT message_dedup_key, COUNT(*)
FROM customer_service_messages
WHERE message_dedup_key IS NOT NULL
GROUP BY message_dedup_key
HAVING COUNT(*) > 1;
```

### 8.3 指标校验

必须对比最近 7 天：

- Dashboard 统一卢布销售额。
- Dashboard 统一卢布广告费。
- RUB 店铺核心指标。
- CNY 店铺原币种核心指标。
- 产品销售明细订单数、访客数、加购率、转化率。
- 广告分析总花费、点击、曝光、订单。
- 客服工单数量、消息数量、未回复数量。

### 8.4 关键口径校验

- WB CNY 店铺广告费历史切换规则：`2026-07-15` 前保持 RUB 原值，`2026-07-15` 起按后台汇率转换到统一卢布。
- `system_settings.cny_to_rub` 优先于 `shops.exchange_rate`。
- v2 raw 保留原币种，view 层提供统一卢布和原币种两种展示口径。

## 9. 双跑方案

阶段 1：MySQL 影子库

```text
生产后端继续读写 SQLite
MySQL 只接受 ETL / shadow sync 写入
前端不切换
```

阶段 2：新同步双写

```text
旧同步 -> legacy SQLite 表
新同步 -> MySQL wb_raw_* / dim_* / fact_*
```

阶段 3：新 view 对比

```text
旧接口结果
  vs
MySQL view_ops_* 结果
```

阶段 4：新模块先接 MySQL

```text
AI 运营助手
站内信
运营任务中心
```

阶段 5：旧页面逐步切换

建议顺序：

1. 产品销售明细。
2. Dashboard。
3. 广告分析。
4. 客服信号。
5. 财务利润。

## 10. 正式切换步骤

正式切换属于高风险操作，必须单独确认。

```text
1. 设置 SYNC_ENABLED=false
2. 重启 backend 使调度暂停
3. 验证 APScheduler 不再运行同步
4. 备份 SQLite volume
5. 执行最后一次增量 ETL
6. 运行校验 SQL
7. 修改 DATABASE_URL=mysql+pymysql://...
8. 重启 backend
9. smoke test：/docs、登录、Dashboard、产品明细、广告、客服
10. 打开 SYNC_ENABLED=true
11. 观察 24-48 小时
12. SQLite 保留只读备份
```

## 11. 回滚方案

切换后若出现 P0 错误：

```text
1. 设置 SYNC_ENABLED=false
2. 修改 DATABASE_URL 回 SQLite
3. 重启 backend
4. 验证旧页面恢复
5. MySQL 保留现场，不做删除
6. 对比切换期间 MySQL 写入数据，必要时补回 SQLite
```

禁止在未确认前执行：

- drop table
- truncate
- 清空 SQLite
- 覆盖 SQLite volume
- 删除 MySQL 影子库

## 12. 下一步建议

建议下一步执行：

1. 生成完整 MySQL DDL 草案。
2. 新增 MySQL 影子库 compose 方案，但不启动生产切换。
3. 写 `01_scan_sqlite_schema.py` 和 `06_validate_migration.py`。
4. 先迁移一份本地/影子 MySQL 验证行数和最近 7 天指标。

执行边界：

- 当前阶段不改生产数据库。
- 当前阶段不重启容器。
- 当前阶段不修改 `DATABASE_URL`。
- 当前阶段不清理任何历史表。
