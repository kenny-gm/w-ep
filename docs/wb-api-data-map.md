# WB API 数据地图与系统重设计草案

更新时间：2026-07-16

目标：基于 WB 官方 API 能提供的数据，映射当前 ERP 已有表和同步代码，明确后续系统化重设计的分层、缺口和优先级。

本文件是设计草案，不包含数据库变更。

## 1. 官方 API 数据域总览

| 数据域 | 官方 API 类目 | 可获取的信息 | 建议用途 |
| --- | --- | --- | --- |
| 店铺/账号 | API information / Users | seller 信息、主体、评分、用户/权限、token 类目 | 店铺档案、权限检查、同步健康检查 |
| 商品内容 | Content | 商品卡、nmId、vendorCode、subject、品牌、类目、特征、尺寸、媒体、标签、错误卡片 | 商品主数据、商品维度字典 |
| 价格折扣 | Prices | 价格、折扣、WB Club 折扣、B2B 折扣、促销日历、促销商品 | 价格监控、促销分析 |
| 库存仓库 | Marketplace / Analytics / Statistics | FBS 仓库库存、WB 仓库库存、仓库列表、库存分析报表 | 库存预警、补货、滞销分析 |
| 订单运营 | Statistics / Marketplace | orders、sales、returns、FBS 组装订单、状态、贴纸、买家信息、metadata | 订单追踪、运营销售统计 |
| 商品漏斗 | Analytics | openCount、cartCount、orderCount、orderSum、搜索词、区域销售、品牌占比 | Dashboard、产品销售明细、转化分析 |
| 广告 | Promotion | 广告活动、广告状态、预算、余额、充值、费用历史、活动统计、搜索词/搜索簇统计 | 广告看板、广告归因、关键词优化 |
| 客服问答 | Feedbacks / Questions | 问答列表、详情、回复、拒绝、未回复数量 | 客服工作台 |
| 客服评价 | Feedbacks | 评价列表、详情、回复/编辑、归档、置顶、按评价退货 | 客服工作台、评分监控 |
| 买家聊天 | Buyers Chat | 聊天列表、事件流、回复、附件下载 | 客服工作台 |
| 买家退货 | Buyers Returns | 退货申请列表、处理动作、归档 | 售后 SLA、退货原因分析 |
| 财务对账 | Finance / Documents | 余额、realization sales report、acquiring、单据列表/下载 | 财务对账、利润核算 |

官方文档入口：

- API 总说明与 token 类目：https://dev.wildberries.ru/en/docs/openapi/api-information
- 商品、价格、库存：https://dev.wildberries.ru/en/docs/openapi/work-with-products
- Analytics：https://dev.wildberries.ru/en/docs/openapi/analytics
- Statistics / Reports：https://dev.wildberries.ru/en/docs/openapi/reports
- Promotion：https://dev.wildberries.ru/en/docs/openapi/promotion
- 客服沟通：https://dev.wildberries.ru/en/docs/openapi/user-communication
- FBS：https://dev.wildberries.ru/en/docs/openapi/orders-fbs
- FBW Supplies：https://dev.wildberries.ru/en/docs/openapi/orders-fbw
- Finance / Documents：https://dev.wildberries.ru/en/docs/openapi/financial-reports-and-accounting

## 2. 当前系统已接入的数据

当前代码证据：

- 模型：`backend/app/models/models.py`
- WB 客户端：`backend/app/services/wb_api.py`
- 同步服务：`backend/app/services/sync.py`
- 客服客户端：`backend/app/services/wb_customer_client.py`
- 客服同步：`backend/app/services/customer_service_sync.py`

当前生产库只读统计（2026-07-16）：

| 表 | 记录数 | 当前含义 |
| --- | ---: | --- |
| shops | 5 | 店铺配置，含 token、平台、币种、汇率 |
| products | 169 | 商品主表，来自 Content / Statistics fallback |
| orders | 2 065 | 当前主要是 analytics 聚合订单和部分订单数据 |
| order_items | 907 | 订单明细，覆盖不完整 |
| ad_records | 30 107 | 同时存广告统计和商品漏斗数据 |
| ad_keyword_stats | 181 785 | 广告关键词/搜索词统计 |
| customer_service_items | 4 606 | 客服统一工单 |
| customer_service_messages | 19 649 | 客服消息明细 |
| customer_service_actions | 24 | 客服动作审计 |
| metric_histories | 0 | 预留但未形成主数据 |
| inventory_snapshots | 0 | 预留但未形成主数据 |
| inventory_records | 0 | 手工库存/成本记录，未接 WB 原始库存 |
| sync_logs | 28 002 | 同步日志 |
| sync_jobs | 7 | 异步同步任务 |

## 3. 现有表与 WB API 映射

| 当前表 | 对应 WB API | 当前用途 | 主要问题 |
| --- | --- | --- | --- |
| shops | 所有 API token 配置 | 店铺配置、币种、汇率、同步开关 | token 类目权限未结构化保存；汇率字段与 system_settings 曾冲突 |
| products | Content cards list；Statistics stocks fallback | 商品列表、负责人、成本、尺寸 | `nm_id` 当前全局唯一，不适合多店铺；缺少 raw_json、subject、brand、barcode 多规格结构 |
| orders | Analytics sales funnel；少量订单逻辑 | 运营订单聚合 | 不是 WB 原始订单；`order_id=analytics_shop_date` 是聚合 ID；缺少 srid/orderUid/saleID |
| order_items | 订单明细 | 利润计算预留 | 与真实 WB 原始订单链路不完整 |
| ad_records | Promotion fullstats；Analytics product funnel | 广告统计 + 商品漏斗混表 | `ad_type=advertising/product_analytics` 混合两类口径；缺少 raw_json、广告活动快照、搜索簇维度 |
| ad_keyword_stats | Promotion normquery/stats | 广告关键词统计 | 数据量大但只覆盖搜索广告；缺少独立广告活动维表 |
| customer_service_items | Questions / Feedbacks / Chat / Returns | 客服统一工单 | 设计方向正确，保留 raw_json；可继续扩展 SLA 和归因 |
| customer_service_messages | Chat events / feedback/question messages | 客服消息 | 设计方向正确，已做 message_dedup_key |
| customer_service_actions | 回复/标记/退货动作 | 审计动作 | 数据量少，后续可补全所有人工动作 |
| inventory_snapshots | Marketplace stocks / Statistics stocks / Analytics inventory | 库存快照预留 | 当前未接入生产数据 |
| metric_histories | Analytics / derived metrics | 产品日指标预留 | 当前未使用；与 ad_records.product_analytics 重叠 |

## 4. 当前设计的核心缺口

### P0：缺少 WB 原始数据层

当前很多表直接存业务计算结果，例如 `ad_records` 既存广告，又存商品销售漏斗。建议新增 raw 层，按 API 类目保存原始响应和关键字段。

建议新增：

- `wb_content_cards_raw`
- `wb_statistics_orders_raw`
- `wb_statistics_sales_raw`
- `wb_analytics_product_funnel_raw`
- `wb_promotion_adverts_raw`
- `wb_promotion_ad_stats_raw`
- `wb_promotion_keyword_stats_raw`
- `wb_finance_realization_reports_raw`
- `wb_inventory_stocks_raw`

### P0：商品主键设计需要调整

当前 `products.nm_id` 是全局唯一。代码里同步商品时，如果同一个 `nm_id` 已存在于其他店铺，会跳过创建：

```text
Product.nm_id == nm_id
```

新设计应改为：

- 业务唯一：`shop_id + nm_id`
- 可选规格唯一：`shop_id + nm_id + barcode`
- 产品名称聚合：用 `custom_name` 或新建 `product_group_id`，不要用 `nm_id` 替代产品组。

### P0：运营口径与财务口径必须分离

建议分三种金额来源：

| 口径 | 数据来源 | 用途 |
| --- | --- | --- |
| 运营订单金额 | Analytics / Statistics | 看板、趋势、预警 |
| 广告费用 | Promotion | 广告看板、广告占比 |
| 财务结算金额 | Finance realization report | 利润、对账、真实收入 |

不要再用一个 `sales` 字段同时承担三种口径。

### P1：广告数据需要活动维表

当前 `ad_records` 存的是明细统计，没有稳定保存广告活动配置快照。

建议新增：

- `wb_ad_campaigns`
- `wb_ad_campaign_products`
- `wb_ad_daily_stats`
- `wb_ad_keyword_daily_stats`
- `wb_ad_budget_events`

这样广告费用、广告类型、投放商品、搜索词、预算变化都能追溯。

### P1：库存与价格折扣还没有形成生产数据链路

官方能提供价格、折扣、库存、仓库、促销信息。当前系统基本没有使用这些数据。

建议后续补：

- `wb_product_prices_daily`
- `wb_product_discounts_daily`
- `wb_inventory_daily`
- `wb_warehouses`
- `wb_promotion_calendar`

这些数据会直接影响补货、利润、促销复盘。

### P1：Finance 未接入，利润不能系统化重做

当前利润计算依赖 `orders`、`order_items`、`inventory_records`，但财务核心 report 未接入。

建议新增：

- `wb_finance_reports`
- `wb_finance_report_lines`
- `wb_finance_documents`
- `wb_acquiring_reports`

利润模块以后应以 Finance report 为最终口径，Analytics / Statistics 只做运营预估。

## 5. 推荐新架构

### 5.1 原始层 raw

原则：按 API 来源落库，保留 `raw_json`，不做业务解释。

命名建议：

```text
wb_raw_content_cards
wb_raw_statistics_orders
wb_raw_statistics_sales
wb_raw_analytics_product_funnel
wb_raw_promotion_adverts
wb_raw_promotion_ad_stats
wb_raw_promotion_keyword_stats
wb_raw_finance_realization
wb_raw_customer_questions
wb_raw_customer_feedbacks
wb_raw_customer_chats
wb_raw_customer_returns
```

通用字段：

```text
id
shop_id
source_api
source_endpoint
external_id
external_updated_at
sync_batch_id
raw_json
created_at
updated_at
```

### 5.2 事实层 facts

原则：统一主键、清洗字段、做币种和时间规范化，但不做复杂展示聚合。

建议：

```text
fact_product_daily
fact_product_shop_daily
fact_order_daily
fact_sales_daily
fact_ad_daily
fact_ad_keyword_daily
fact_inventory_daily
fact_finance_sales
fact_customer_service_daily
```

### 5.3 维表 dimensions

建议：

```text
dim_shop
dim_product
dim_product_group
dim_product_variant
dim_ad_campaign
dim_warehouse
dim_currency_rate
dim_owner
```

### 5.4 展示层 views / API

用于前端和钉钉/AI 表格同步：

```text
view_dashboard_metrics
view_dashboard_trend
view_product_sales_detail
view_ad_analysis
view_customer_service_inbox
view_finance_reconciliation
```

## 6. 同步任务拆分建议

| 同步任务 | API 来源 | 建议频率 | 写入层 |
| --- | --- | --- | --- |
| 商品卡同步 | Content | 每日 1-2 次 | raw + dim_product |
| 商品漏斗同步 | Analytics | 1-3 小时 | raw + fact_product_daily |
| Statistics 订单/销售 | Statistics | 30-60 分钟 | raw + fact_order_daily |
| 广告活动配置 | Promotion adverts | 30-60 分钟 | raw + dim_ad_campaign |
| 广告统计 | Promotion stats | 30-60 分钟 | raw + fact_ad_daily |
| 广告关键词 | Promotion normquery | 1-3 小时 | raw + fact_ad_keyword_daily |
| 库存 | Marketplace / Analytics | 1-3 小时 | raw + fact_inventory_daily |
| 价格折扣 | Prices | 每日 / 促销期加频 | raw + dim_product_price |
| 客服问答评价 | Feedbacks / Questions | 3-10 分钟 | raw + customer_service_* |
| 买家聊天 | Buyers Chat events | 1-5 分钟 | raw + customer_service_* |
| 退货申请 | Buyers Returns | 5-15 分钟 | raw + customer_service_* |
| 财务 report | Finance | 每日 / 每周 | raw + fact_finance_sales |

## 7. 产品销售明细重设计建议

产品销售明细不建议直接依赖 `ad_records` 混合表。建议后端输出一个专门 view：

```text
view_product_sales_detail
```

维度：

```text
date
owner
product_group_id
custom_name
shop_id
nm_id
sku/barcode
currency
```

指标：

```text
sales_native
sales_rub
orders
visitors
cart_count
cart_rate
conversion_rate
ad_cost_native
ad_cost_rub
ad_orders
ad_clicks
ad_views
ad_ctr
ad_cart_count
ad_cost_ratio
```

展示层可以同时支持：

- 主表：产品组维度，统一卢布排序。
- 展开：店铺 + nmId + sku 原币种明细。
- 再展开：日期明细。

这样保留现有运营习惯，同时解决跨店铺、跨币种、跨产品 ID 混淆。

## 8. 实施优先级

### Phase 1：先补数据地图，不动生产展示

- 新建 raw 表设计草案。
- 梳理现有字段到新字段的映射。
- 输出迁移/双写方案。

### Phase 2：商品和销售口径重构

- 解除 `products.nm_id` 全局唯一设计。
- 新增 `product_group` 概念。
- 商品漏斗从 `ad_records` 拆到 `fact_product_daily`。

### Phase 3：广告口径重构

- 广告活动、广告统计、关键词统计拆表。
- `ad_records` 逐步降级为兼容表或历史表。

### Phase 4：财务口径接入

- 接 Finance realization report。
- 建利润和财务对账模块。
- 明确运营收入、广告费用、结算收入三套口径。

### Phase 5：前端重做

- Dashboard 使用 view 层，不直接读混合表。
- 产品销售明细改为产品组 -> 店铺 -> 日期三层。
- 广告分析按活动/商品/关键词三层追溯。

## 9. 当前结论

当前系统不是不能继续修，而是销售、广告、商品三个核心域已经到达“必须分层”的阶段。

最稳的路线不是直接重写，而是：

1. 保留现有表和看板。
2. 新增 raw/fact/view 三层。
3. 新同步任务先双写。
4. 对比新旧 view 数字。
5. 验证稳定后再切换前端。

这样可以避免影响当前运营使用，也能逐步把数据口径理清。
