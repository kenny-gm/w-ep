-- Migration: 001_add_platform_config.sql
-- 为 shops 表添加 platform_config 列
-- 适用于 SQLite 和 PostgreSQL

-- SQLite
-- ALTER TABLE shops ADD COLUMN platform_config TEXT DEFAULT '{}';

-- PostgreSQL
ALTER TABLE shops ADD COLUMN IF NOT EXISTS platform_config JSON DEFAULT '{}';

-- 验证
-- SELECT name, sql FROM sqlite_master WHERE type='table' AND name='shops';
