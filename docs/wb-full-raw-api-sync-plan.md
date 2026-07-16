# WB API 全量 Raw 原始层同步执行方案

更新时间：2026-07-16

## 目标

把 WB API 能读取到的原始响应完整落到 MySQL 影子库 `wb_erp_shadow` 的 `wb_raw_*` 表中，作为后续 `dim_* / fact_* / view_ops_* / AI 运营分析 / 任务系统` 的可信数据源。

本阶段只建设影子库 raw 层，不切换生产库，不改生产 SQLite，不影响现有前端。

## 现场扫描结果

- 真实仓库：`/opt/wb-erp`
- 生产后端当前数据库：`sqlite:////app/db/wb_erp.db`
- MySQL 影子库：`wb_erp_shadow`
- MySQL v2 schema：已创建，含 46 张表、4 个 view
- 已完成最近 7 天 `dim_* / fact_* / view_ops_*` 迁移校验：`34 passed, 0 failed`
- 当前 WB 店铺：4 个，且均配置 token
  - `炊恒WB`：CNY
  - `116WB`：RUB
  - `157WB`：RUB
  - `邢拓WB`：CNY

## 现有客户端覆盖范围

### `backend/app/services/wb_api.py`

已覆盖：

- `common-api.wildberries.ru`
  - `/api/v1/seller-info`
- `content-api.wildberries.ru`
  - `/content/v2/get/cards/list`
- `marketplace-api.wildberries.ru`
  - `/api/v3/orders/new`
  - `/api/v3/orders`
  - `/api/v3/warehouses`
  - `/api/v3/stocks`
- `seller-analytics-api.wildberries.ru`
  - `/api/analytics/v3/sales-funnel/products/history`
  - `/api/v1/sales-funnel`
  - `/api/v2/nm-report`
- `statistics-api.wildberries.ru`
  - `/api/v1/supplier/stocks`
- `advert-api.wildberries.ru`
  - `/api/advert/v2/adverts`
  - `/adv/v3/fullstats`
  - `/adv/v1/normquery/stats`

已定义但当前未完整落 raw：

- prices / discounts
- finance realization / documents
- supplies
- analytics search terms
- promotion budgets / payments / recommendations

### `backend/app/services/wb_customer_client.py`

已覆盖：

- `feedbacks-api.wildberries.ru`
  - `/api/v1/questions`
  - `/api/v1/question`
  - `/api/v1/feedbacks`
  - `/api/v1/feedback`
- `buyer-chat-api.wildberries.ru`
  - `/api/v1/seller/chats`
  - `/api/v1/seller/events`
- `returns-api.wildberries.ru`
  - `/api/v1/claims`

## 全量 Raw 分批顺序

不能一口气全量跑。按风险、限流、业务价值拆 6 批。

### Batch 0：权限探测和最小 raw 样本

目的：确认每个店铺 token 对各 API 类目的权限，不拉大数据。

每个 WB 店铺调用：

- seller-info：1 次
- content cards：第一页，limit 10
- adverts：1 次
- marketplace new orders：1 次
- questions：take 1
- feedbacks：take 1
- chats：limit 1
- returns：limit 1

写入：

- `wb_raw_api_responses`
- `wb_raw_content_cards`
- `wb_raw_promotion_campaigns`
- `wb_raw_customer_questions`
- `wb_raw_customer_feedbacks`
- `wb_raw_customer_chats`
- `wb_raw_customer_returns`

通过标准：

- 每个店铺生成权限矩阵
- 401/403/429 单独记录，不中断其他店铺
- raw 表有 `sync_batch_id`
- 不改生产 SQLite

### Batch 1：商品和基础维度 raw

目的：建立完整商品原始层。

接口：

- Content 商品卡全量分页
- Statistics stocks 作为商品/条码兜底
- Marketplace warehouses / stocks

写入：

- `wb_raw_content_cards`
- `wb_raw_inventory_stocks`

后续生成：

- `dim_product`
- `dim_product_variant`
- `dim_warehouse`

### Batch 2：销售和漏斗 raw

目的：补齐运营销售和漏斗。

接口：

- Statistics orders / sales
- Analytics product funnel history
- Analytics nm-report

写入：

- `wb_raw_statistics_orders`
- `wb_raw_statistics_sales`
- `wb_raw_analytics_product_funnel`

注意：

- Statistics 历史通常不超过 90 天，按官方限制执行。
- Analytics 限流低，按店铺、日期窗口、nm_id 分批。

### Batch 3：广告 raw

目的：补齐广告活动、广告统计、关键词/搜索簇。

接口：

- adverts
- fullstats
- normquery/stats

写入：

- `wb_raw_promotion_campaigns`
- `wb_raw_promotion_stats`
- `wb_raw_promotion_keywords`

注意：

- Promotion 当前限流按 3 次/分钟执行。
- 每次最多 50 个 advert_id。

### Batch 4：客服 raw

目的：保留客服原始上下文，但先不迁正文大表到生产。

接口：

- questions
- feedbacks
- buyer chats
- buyer events
- returns claims

写入：

- `wb_raw_customer_questions`
- `wb_raw_customer_feedbacks`
- `wb_raw_customer_chats`
- `wb_raw_customer_returns`

注意：

- 聊天事件必须保留 cursor。
- 不复用旧同步的危险 cursor 写法。
- 只写 MySQL 影子库 raw，不覆盖 `customer_service_*` 生产表。

### Batch 5：财务 raw

目的：建立财务对账原始层。

接口：

- realization reports
- report details
- documents
- acquiring reports

写入：

- `wb_raw_finance_realization_reports`
- `wb_raw_finance_documents`

注意：

- 财务口径最后接入事实层。
- 不用 Statistics 销售额做最终利润。

## 执行边界

全量 raw 同步必须满足：

- 不改 `DATABASE_URL`
- 不重启 backend/frontend
- 不写生产 SQLite
- 不调用任何 WB 写接口
- 不改价格、库存、广告预算、客服回复
- 所有写入只进 MySQL 影子库
- 每批有 `sync_batch_id`
- 每批可重复执行，不翻倍
- 每批结束后跑 raw 行数和错误统计

## 脚本设计

建议新增：

```text
backend/scripts/mysql_migration/08_sync_wb_raw_from_api.py
```

默认 dry-run，不调用 WB API。

参数：

```bash
--phase permission_probe|content|sales|ads|customer|finance|all
--shop-id 1
--days 7
--apply
--max-pages 1
--batch-id wbraw_YYYYMMDD_HHMMSS
```

默认行为：

- 无 `--apply`：只打印计划、店铺、预计 API 类目、目标 raw 表。
- 有 `--apply`：才调用 WB API 并写 MySQL 影子库。

## 下一步

建议先实现并执行 Batch 0：

```bash
docker exec wb-erp-backend python /app/backend/scripts/mysql_migration/08_sync_wb_raw_from_api.py
docker exec wb-erp-backend python /app/backend/scripts/mysql_migration/08_sync_wb_raw_from_api.py --phase permission_probe --max-pages 1 --apply
```

Batch 0 成功后，再按 Content -> Sales/Analytics -> Ads -> Customer -> Finance 的顺序推进。
