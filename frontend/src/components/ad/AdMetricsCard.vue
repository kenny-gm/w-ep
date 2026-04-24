<template>
  <el-row :gutter="16" class="metrics-row">
    <!-- 广告花费 -->
    <el-col :xs="12" :sm="6">
      <el-card class="metric-card spend-card">
        <div class="metric-content">
          <div class="metric-icon">💰</div>
          <div class="metric-label">广告花费</div>
          <div class="metric-value">¥{{ formatNumber(metrics.ad_spend) }}</div>
        </div>
      </el-card>
    </el-col>

    <!-- ROAS -->
    <el-col :xs="12" :sm="6">
      <el-card class="metric-card roas-card">
        <div class="metric-content">
          <div class="metric-icon">📈</div>
          <div class="metric-label">ROAS</div>
          <div class="metric-value" :class="getMetricClass(metrics.roas, [3.5, 5])">
            {{ metrics.roas?.toFixed(1) || '-' }}
          </div>
          <div class="metric-hint">目标 ≥ 3.5</div>
        </div>
      </el-card>
    </el-col>

    <!-- ACOS -->
    <el-col :xs="12" :sm="6">
      <el-card class="metric-card acos-card">
        <div class="metric-content">
          <div class="metric-icon">📉</div>
          <div class="metric-label">ACOS</div>
          <div class="metric-value" :class="getAcosClass(metrics.acos)">
            {{ (metrics.acos || 0).toFixed(1) }}%
          </div>
          <div class="metric-hint">目标 ≤ 20%</div>
        </div>
      </el-card>
    </el-col>

    <!-- 广告订单 -->
    <el-col :xs="12" :sm="6">
      <el-card class="metric-card orders-card">
        <div class="metric-content">
          <div class="metric-icon">🛒</div>
          <div class="metric-label">广告订单</div>
          <div class="metric-value">{{ metrics.ad_orders }}</div>
          <div class="metric-hint">占比 {{ metrics.ad_orders_ratio?.toFixed(1) || 0 }}%</div>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
const props = defineProps({
  metrics: {
    type: Object,
    default: () => ({
      ad_spend: 0,
      roas: 0,
      acos: 0,
      ad_orders: 0,
      ad_orders_ratio: 0
    })
  }
})

function formatNumber(num) {
  if (!num) return '0'
  return num.toLocaleString('zh-CN')
}

function getMetricClass(value, thresholds) {
  if (!value) return ''
  const [good, excellent] = thresholds
  if (value >= excellent) return 'excellent'
  if (value >= good) return 'good'
  return 'warning'
}

function getAcosClass(value) {
  if (!value) return ''
  if (value <= 0.15) return 'excellent'
  if (value <= 0.25) return 'good'
  return 'warning'
}
</script>

<style scoped>
/* 极简纯白全局样式 */
.minimal-white {
  padding: 16px;
  
  background: #f8fafc;
  color: #0f172a;
}

/* 白色卡片 */
.el-card, .card, .metric-card, .chart-card, .table-card {
  background: white !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}

/* 按钮 - 深色主题 */
.el-button--primary {
  background: #0f172a !important;
  border-color: #0f172a !important;
}
.el-button--primary:hover {
  background: #334155 !important;
}

/* 筛选栏 */
.filter-bar, .filter-section {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
}

/* 表格 */
.el-table {
  --el-table-bg-color: white;
  --el-table-tr-bg-color: white;
  --el-table-header-bg-color: #f8fafc;
  --el-table-row-hover-bg-color: #f8fafc;
  --el-table-border-color: #e2e8f0;
  --el-table-text-color: #334155;
  --el-table-header-text-color: #475569;
}

/* 对话框 */
.el-dialog {
  background: white !important;
  border-radius: 12px;
}
.el-dialog__title {
  color: #0f172a !important;
}

/* 输入框 */
.el-input__wrapper {
  background: white !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: none !important;
}

/* 文字颜色 */
h1, h2, h3, h4, h5, h6, p, span, div {
  color: #0f172a;
}

/* 次要文字 */
.text-muted, .subtitle, .desc, .label {
  color: #64748b !important;
}

/* 正面绿色 */
.positive, .up, .growth {
  color: #16a34a !important;
}

/* 负面红色 */
.negative, .down, .decline {
  color: #dc2626 !important;
}

/* 分页 */
.el-pagination {
  justify-content: flex-end;
}



.metrics-row {
  margin-bottom: 20px;
}

.metric-card {
  height: 100%;
  text-align: center;
}

.metric-content {
  padding: 12px 0;
}

.metric-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.metric-value.excellent {
  color: #67c23a;
}

.metric-value.good {
  color: #8b5cf6;
}

.metric-value.warning {
  color: #e6a23c;
}

.metric-hint {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}

/* 卡片边框颜色 */
.spend-card {
  border-top: 3px solid #e6a23c;
}

.roas-card {
  border-top: 3px solid #67c23a;
}

.acos-card {
  border-top: 3px solid #409eff;
}

.orders-card {
  border-top: 3px solid #8b5cf6;
}
</style>
