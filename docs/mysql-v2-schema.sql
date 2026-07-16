-- MySQL v2 schema draft for WB ERP
-- Generated: 2026-07-16
--
-- Purpose:
--   1. Keep legacy tables for current pages.
--   2. Add v2 raw/dim/fact/view/ops layers for WB API full-field redesign.
--   3. Support shadow MySQL validation before production cutover.
--
-- This file is a DDL draft. Do not run against production without a separate
-- migration execution plan, SQLite backup, and explicit confirmation.

SET NAMES utf8mb4;
SET time_zone = '+08:00';

-- ---------------------------------------------------------------------------
-- Migration control
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS migration_batches (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  batch_key VARCHAR(100) NOT NULL,
  source_db VARCHAR(300) NOT NULL,
  target_db VARCHAR(300) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'pending',
  started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at DATETIME NULL,
  source_rows BIGINT NOT NULL DEFAULT 0,
  target_rows BIGINT NOT NULL DEFAULT 0,
  result_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_migration_batches_key (batch_key),
  KEY ix_migration_batches_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS migration_errors (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  batch_id BIGINT NULL,
  source_table VARCHAR(100) NOT NULL,
  source_pk VARCHAR(200) NULL,
  error_type VARCHAR(80) NOT NULL,
  error_message TEXT NOT NULL,
  source_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY ix_migration_errors_batch (batch_id),
  KEY ix_migration_errors_source (source_table, source_pk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- Raw layer
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS wb_raw_api_responses (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  platform VARCHAR(30) NOT NULL DEFAULT 'wildberries',
  source_api VARCHAR(50) NOT NULL,
  source_endpoint VARCHAR(200) NOT NULL,
  external_id VARCHAR(200) NULL,
  sync_batch_id VARCHAR(100) NOT NULL,
  request_params_json JSON NULL,
  external_created_at DATETIME NULL,
  external_updated_at DATETIME NULL,
  raw_json JSON NOT NULL,
  raw_hash CHAR(64) NULL,
  fetched_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY ix_raw_api_shop_source (shop_id, source_api, fetched_at),
  KEY ix_raw_api_external (source_api, external_id),
  KEY ix_raw_api_batch (sync_batch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS wb_raw_content_cards LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_prices LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_discounts LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_inventory_stocks LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_statistics_orders LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_statistics_sales LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_analytics_product_funnel LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_analytics_search_terms LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_promotion_campaigns LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_promotion_stats LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_promotion_keywords LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_customer_questions LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_customer_feedbacks LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_customer_chats LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_customer_returns LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_finance_realization_reports LIKE wb_raw_api_responses;
CREATE TABLE IF NOT EXISTS wb_raw_finance_documents LIKE wb_raw_api_responses;

-- ---------------------------------------------------------------------------
-- Dimensions
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_shop (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  legacy_shop_id BIGINT NULL,
  platform VARCHAR(30) NOT NULL DEFAULT 'wildberries',
  name VARCHAR(100) NOT NULL,
  seller_external_id VARCHAR(100) NULL,
  seller_name VARCHAR(200) NULL,
  tin VARCHAR(80) NULL,
  currency VARCHAR(10) NOT NULL DEFAULT 'RUB',
  cny_to_rub_rate DECIMAL(18,6) NULL,
  token_permissions_json JSON NULL,
  token_checked_at DATETIME NULL,
  sync_enabled TINYINT(1) NOT NULL DEFAULT 1,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_dim_shop_legacy (legacy_shop_id),
  KEY ix_dim_shop_platform_active (platform, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dim_owner (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  owner_name VARCHAR(100) NOT NULL,
  user_id BIGINT NULL,
  role VARCHAR(50) NULL,
  allowed_shops_json JSON NULL,
  allowed_products_json JSON NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_dim_owner_name (owner_name),
  KEY ix_dim_owner_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dim_product (
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
  length_cm DECIMAL(12,3) NULL,
  width_cm DECIMAL(12,3) NULL,
  height_cm DECIMAL(12,3) NULL,
  weight_kg DECIMAL(12,3) NULL,
  purchase_price_cny DECIMAL(18,2) NULL,
  shipping_price_cny DECIMAL(18,2) NULL,
  raw_card_id BIGINT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_dim_product_shop_nm (shop_id, nm_id),
  UNIQUE KEY uq_dim_product_legacy (legacy_product_id),
  KEY ix_dim_product_owner (owner),
  KEY ix_dim_product_custom_name (custom_name),
  KEY ix_dim_product_sku (sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dim_product_variant (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id BIGINT NOT NULL,
  shop_id BIGINT NOT NULL,
  nm_id VARCHAR(50) NOT NULL,
  barcode VARCHAR(120) NOT NULL,
  chrt_id VARCHAR(80) NULL,
  size_name VARCHAR(100) NULL,
  color_name VARCHAR(100) NULL,
  sku VARCHAR(120) NULL,
  raw_card_id BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_dim_variant_barcode (shop_id, nm_id, barcode),
  KEY ix_dim_variant_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dim_product_group (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  group_name VARCHAR(500) NOT NULL,
  owner VARCHAR(100) NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_dim_product_group_name (group_name),
  KEY ix_dim_product_group_owner (owner)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dim_product_group_member (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_group_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  shop_id BIGINT NOT NULL,
  nm_id VARCHAR(50) NOT NULL,
  is_primary TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_group_member_product (product_group_id, product_id),
  UNIQUE KEY uq_group_member_shop_nm (product_group_id, shop_id, nm_id),
  KEY ix_group_member_product (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dim_ad_campaign (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  advert_id BIGINT NOT NULL,
  campaign_name VARCHAR(300) NULL,
  campaign_type VARCHAR(80) NULL,
  status VARCHAR(50) NULL,
  payment_type VARCHAR(30) NULL,
  placements VARCHAR(100) NULL,
  budget DECIMAL(18,2) NULL,
  currency VARCHAR(10) NOT NULL DEFAULT 'RUB',
  last_external_updated_at DATETIME NULL,
  raw_campaign_id BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_dim_ad_campaign (shop_id, advert_id),
  KEY ix_dim_ad_campaign_status (shop_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dim_warehouse (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  warehouse_external_id VARCHAR(100) NOT NULL,
  warehouse_name VARCHAR(200) NULL,
  warehouse_type VARCHAR(50) NULL,
  region_name VARCHAR(200) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_dim_warehouse (shop_id, warehouse_external_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dim_currency_rate (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  currency_from VARCHAR(10) NOT NULL,
  currency_to VARCHAR(10) NOT NULL,
  effective_date DATE NOT NULL,
  rate DECIMAL(18,6) NOT NULL,
  source VARCHAR(50) NOT NULL DEFAULT 'system_settings',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_currency_rate_date (currency_from, currency_to, effective_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- Facts
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_product_daily (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  product_group_id BIGINT NULL,
  nm_id VARCHAR(50) NOT NULL,
  biz_date DATE NOT NULL,
  order_count INT NOT NULL DEFAULT 0,
  sales_amount DECIMAL(18,2) NOT NULL DEFAULT 0,
  sales_currency VARCHAR(10) NOT NULL DEFAULT 'RUB',
  sales_amount_rub DECIMAL(18,2) NOT NULL DEFAULT 0,
  return_count INT NOT NULL DEFAULT 0,
  cancel_count INT NOT NULL DEFAULT 0,
  source_raw_id BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_fact_product_daily (shop_id, nm_id, biz_date),
  KEY ix_fact_product_daily_product_date (product_id, biz_date),
  KEY ix_fact_product_daily_group_date (product_group_id, biz_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_product_funnel_daily (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  product_group_id BIGINT NULL,
  nm_id VARCHAR(50) NOT NULL,
  biz_date DATE NOT NULL,
  impressions INT NOT NULL DEFAULT 0,
  visitors INT NOT NULL DEFAULT 0,
  clicks INT NOT NULL DEFAULT 0,
  cart_count INT NOT NULL DEFAULT 0,
  order_count INT NOT NULL DEFAULT 0,
  sales_amount DECIMAL(18,2) NOT NULL DEFAULT 0,
  sales_currency VARCHAR(10) NOT NULL DEFAULT 'RUB',
  sales_amount_rub DECIMAL(18,2) NOT NULL DEFAULT 0,
  source_raw_id BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_product_funnel_day (shop_id, nm_id, biz_date),
  KEY ix_product_funnel_product_date (product_id, biz_date),
  KEY ix_product_funnel_group_date (product_group_id, biz_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_ad_daily (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  product_id BIGINT NULL,
  product_group_id BIGINT NULL,
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
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_ad_daily (shop_id, advert_id, nm_id, biz_date, payment_type, placements),
  KEY ix_ad_daily_product_date (product_id, biz_date),
  KEY ix_ad_daily_group_date (product_group_id, biz_date),
  KEY ix_ad_daily_shop_date (shop_id, biz_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_ad_keyword_daily (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  product_id BIGINT NULL,
  product_group_id BIGINT NULL,
  advert_id BIGINT NOT NULL,
  nm_id VARCHAR(50) NOT NULL,
  keyword VARCHAR(500) NOT NULL,
  platform VARCHAR(30) NOT NULL DEFAULT 'search',
  biz_date DATE NOT NULL,
  impressions INT NOT NULL DEFAULT 0,
  clicks INT NOT NULL DEFAULT 0,
  order_count INT NOT NULL DEFAULT 0,
  cart_count INT NOT NULL DEFAULT 0,
  spend DECIMAL(18,2) NOT NULL DEFAULT 0,
  spend_currency VARCHAR(10) NOT NULL DEFAULT 'RUB',
  spend_rub DECIMAL(18,2) NOT NULL DEFAULT 0,
  avg_position DECIMAL(12,4) NULL,
  payment_type VARCHAR(30) NULL,
  source_raw_id BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_ad_keyword_daily (shop_id, advert_id, nm_id, keyword, biz_date, platform),
  KEY ix_ad_keyword_daily_product_date (product_id, biz_date),
  KEY ix_ad_keyword_daily_advert_date (advert_id, biz_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_inventory_daily (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  variant_id BIGINT NULL,
  warehouse_id BIGINT NULL,
  nm_id VARCHAR(50) NOT NULL,
  barcode VARCHAR(120) NULL,
  biz_date DATE NOT NULL,
  quantity INT NOT NULL DEFAULT 0,
  quantity_full INT NOT NULL DEFAULT 0,
  in_way_to_client INT NOT NULL DEFAULT 0,
  in_way_from_client INT NOT NULL DEFAULT 0,
  source_raw_id BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_inventory_daily (shop_id, nm_id, barcode, warehouse_id, biz_date),
  KEY ix_inventory_daily_product_date (product_id, biz_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_customer_signal_daily (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  product_id BIGINT NULL,
  product_group_id BIGINT NULL,
  nm_id VARCHAR(50) NULL,
  biz_date DATE NOT NULL,
  question_count INT NOT NULL DEFAULT 0,
  feedback_count INT NOT NULL DEFAULT 0,
  chat_count INT NOT NULL DEFAULT 0,
  return_claim_count INT NOT NULL DEFAULT 0,
  negative_feedback_count INT NOT NULL DEFAULT 0,
  avg_rating DECIMAL(8,4) NULL,
  unanswered_count INT NOT NULL DEFAULT 0,
  overdue_count INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_customer_signal_daily (shop_id, nm_id, biz_date),
  KEY ix_customer_signal_product_date (product_id, biz_date),
  KEY ix_customer_signal_group_date (product_group_id, biz_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_finance_daily (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  product_id BIGINT NULL,
  nm_id VARCHAR(50) NULL,
  biz_date DATE NOT NULL,
  report_id VARCHAR(100) NULL,
  sale_amount DECIMAL(18,2) NOT NULL DEFAULT 0,
  commission_amount DECIMAL(18,2) NOT NULL DEFAULT 0,
  logistics_amount DECIMAL(18,2) NOT NULL DEFAULT 0,
  storage_amount DECIMAL(18,2) NOT NULL DEFAULT 0,
  penalty_amount DECIMAL(18,2) NOT NULL DEFAULT 0,
  acquiring_amount DECIMAL(18,2) NOT NULL DEFAULT 0,
  payout_amount DECIMAL(18,2) NOT NULL DEFAULT 0,
  currency VARCHAR(10) NOT NULL DEFAULT 'RUB',
  payout_amount_rub DECIMAL(18,2) NOT NULL DEFAULT 0,
  source_raw_id BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY ix_finance_daily_shop_date (shop_id, biz_date),
  KEY ix_finance_daily_product_date (product_id, biz_date),
  KEY ix_finance_daily_report (report_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fact_sync_health (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  shop_id BIGINT NOT NULL,
  source_api VARCHAR(50) NOT NULL,
  sync_type VARCHAR(50) NOT NULL,
  status VARCHAR(30) NOT NULL,
  records_count BIGINT NOT NULL DEFAULT 0,
  started_at DATETIME NULL,
  finished_at DATETIME NULL,
  error_message TEXT NULL,
  sync_batch_id VARCHAR(100) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY ix_sync_health_shop_type (shop_id, sync_type, finished_at),
  KEY ix_sync_health_status (status, finished_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- Ops workflow layer
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS internal_messages (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  recipient_user_id BIGINT NULL,
  recipient_owner VARCHAR(100) NULL,
  sender_user_id BIGINT NULL,
  message_type VARCHAR(50) NOT NULL,
  title VARCHAR(300) NOT NULL,
  content TEXT NOT NULL,
  related_task_id BIGINT NULL,
  related_suggestion_id BIGINT NULL,
  priority VARCHAR(20) NOT NULL DEFAULT 'normal',
  is_read TINYINT(1) NOT NULL DEFAULT 0,
  read_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY ix_internal_messages_user_read (recipient_user_id, is_read, created_at),
  KEY ix_internal_messages_owner_read (recipient_owner, is_read, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ops_ai_suggestions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  suggestion_key VARCHAR(120) NULL,
  source_view VARCHAR(100) NOT NULL,
  suggestion_type VARCHAR(50) NOT NULL,
  severity VARCHAR(20) NOT NULL DEFAULT 'normal',
  shop_id BIGINT NULL,
  product_id BIGINT NULL,
  product_group_id BIGINT NULL,
  nm_id VARCHAR(50) NULL,
  advert_id BIGINT NULL,
  assignee_owner VARCHAR(100) NULL,
  title VARCHAR(300) NOT NULL,
  ai_summary TEXT NOT NULL,
  ai_reason TEXT NULL,
  ai_suggested_actions JSON NULL,
  metrics_snapshot_json JSON NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'pending',
  converted_task_id BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_ai_suggestion_key (suggestion_key),
  KEY ix_ai_suggestions_owner_status (assignee_owner, status),
  KEY ix_ai_suggestions_product (product_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ops_tasks (
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
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY ix_ops_tasks_assignee_status (assignee_owner, status),
  KEY ix_ops_tasks_user_status (assignee_user_id, status),
  KEY ix_ops_tasks_due_status (due_at, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ops_task_links (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  task_id BIGINT NOT NULL,
  link_type VARCHAR(50) NOT NULL,
  shop_id BIGINT NULL,
  product_id BIGINT NULL,
  product_group_id BIGINT NULL,
  nm_id VARCHAR(50) NULL,
  advert_id BIGINT NULL,
  customer_service_item_id BIGINT NULL,
  finance_report_id VARCHAR(100) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY ix_task_links_task (task_id),
  KEY ix_task_links_product (product_id),
  KEY ix_task_links_customer (customer_service_item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ops_task_comments (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  task_id BIGINT NOT NULL,
  user_id BIGINT NULL,
  owner_name VARCHAR(100) NULL,
  comment_text TEXT NOT NULL,
  attachments_json JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY ix_task_comments_task (task_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ops_task_actions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  task_id BIGINT NOT NULL,
  user_id BIGINT NULL,
  action_type VARCHAR(50) NOT NULL,
  before_json JSON NULL,
  after_json JSON NULL,
  action_note TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY ix_task_actions_task (task_id, created_at),
  KEY ix_task_actions_user (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ops_task_checklists (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  task_id BIGINT NOT NULL,
  item_text VARCHAR(500) NOT NULL,
  is_done TINYINT(1) NOT NULL DEFAULT 0,
  done_by BIGINT NULL,
  done_at DATETIME NULL,
  sort_order INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY ix_task_checklists_task (task_id, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ops_task_templates (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  template_name VARCHAR(200) NOT NULL,
  task_type VARCHAR(50) NOT NULL,
  default_priority VARCHAR(20) NOT NULL DEFAULT 'normal',
  default_due_hours INT NULL,
  checklist_json JSON NULL,
  acceptance_criteria TEXT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_by BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY ix_task_templates_type (task_type, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ops_task_review_snapshots (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  task_id BIGINT NOT NULL,
  snapshot_type VARCHAR(30) NOT NULL,
  snapshot_at DATETIME NOT NULL,
  metrics_snapshot_json JSON NOT NULL,
  ai_review_summary TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY ix_task_review_snapshots_task (task_id, snapshot_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- Views
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW view_ops_product_daily AS
SELECT
  p.product_group_id,
  p.shop_id,
  p.product_id,
  p.nm_id,
  p.biz_date,
  p.order_count,
  p.sales_amount,
  p.sales_currency,
  p.sales_amount_rub,
  COALESCE(f.visitors, 0) AS visitors,
  COALESCE(f.cart_count, 0) AS cart_count,
  COALESCE(f.impressions, 0) AS impressions,
  CASE WHEN COALESCE(f.visitors, 0) > 0 THEN COALESCE(f.cart_count, 0) / f.visitors ELSE 0 END AS cart_rate,
  CASE WHEN COALESCE(f.visitors, 0) > 0 THEN p.order_count / f.visitors ELSE 0 END AS conversion_rate
FROM fact_product_daily p
LEFT JOIN fact_product_funnel_daily f
  ON f.shop_id = p.shop_id
 AND f.nm_id = p.nm_id
 AND f.biz_date = p.biz_date;

CREATE OR REPLACE VIEW view_ops_ad_efficiency AS
SELECT
  a.shop_id,
  a.product_id,
  a.product_group_id,
  a.nm_id,
  a.advert_id,
  a.biz_date,
  a.impressions,
  a.clicks,
  a.visitors,
  a.cart_count,
  a.order_count,
  a.ad_cost,
  a.ad_cost_currency,
  a.ad_cost_rub,
  a.sales_amount,
  a.sales_amount_rub,
  CASE WHEN a.impressions > 0 THEN a.clicks / a.impressions ELSE 0 END AS ctr,
  CASE WHEN a.clicks > 0 THEN a.ad_cost_rub / a.clicks ELSE 0 END AS cpc_rub,
  CASE WHEN a.sales_amount_rub > 0 THEN a.ad_cost_rub / a.sales_amount_rub ELSE 0 END AS ad_ratio
FROM fact_ad_daily a;

CREATE OR REPLACE VIEW view_ops_overview AS
SELECT
  d.biz_date,
  d.shop_id,
  SUM(d.sales_amount_rub) AS sales_amount_rub,
  SUM(d.order_count) AS order_count,
  SUM(COALESCE(f.visitors, 0)) AS visitors,
  SUM(COALESCE(f.cart_count, 0)) AS cart_count,
  SUM(COALESCE(a.ad_cost_rub, 0)) AS ad_cost_rub,
  CASE WHEN SUM(COALESCE(f.visitors, 0)) > 0 THEN SUM(COALESCE(f.cart_count, 0)) / SUM(COALESCE(f.visitors, 0)) ELSE 0 END AS cart_rate,
  CASE WHEN SUM(COALESCE(f.visitors, 0)) > 0 THEN SUM(d.order_count) / SUM(COALESCE(f.visitors, 0)) ELSE 0 END AS conversion_rate,
  CASE WHEN SUM(d.sales_amount_rub) > 0 THEN SUM(COALESCE(a.ad_cost_rub, 0)) / SUM(d.sales_amount_rub) ELSE 0 END AS ad_ratio
FROM fact_product_daily d
LEFT JOIN fact_product_funnel_daily f
  ON f.shop_id = d.shop_id
 AND f.nm_id = d.nm_id
 AND f.biz_date = d.biz_date
LEFT JOIN (
  SELECT shop_id, nm_id, biz_date, SUM(ad_cost_rub) AS ad_cost_rub
  FROM fact_ad_daily
  GROUP BY shop_id, nm_id, biz_date
) a
  ON a.shop_id = d.shop_id
 AND a.nm_id = d.nm_id
 AND a.biz_date = d.biz_date
GROUP BY d.biz_date, d.shop_id;

CREATE OR REPLACE VIEW view_ops_customer_signals AS
SELECT
  c.shop_id,
  c.product_id,
  c.product_group_id,
  c.nm_id,
  c.biz_date,
  c.question_count,
  c.feedback_count,
  c.chat_count,
  c.return_claim_count,
  c.negative_feedback_count,
  c.avg_rating,
  c.unanswered_count,
  c.overdue_count,
  CASE
    WHEN c.overdue_count > 0 THEN 'urgent'
    WHEN c.negative_feedback_count > 0 OR c.return_claim_count > 0 THEN 'high'
    WHEN c.unanswered_count > 0 THEN 'normal'
    ELSE 'low'
  END AS signal_level
FROM fact_customer_signal_daily c;

