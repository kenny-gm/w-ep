<template>
  <div class="core-metrics minimal-white">
    <el-row :gutter="16">
      <!-- 花费指标 -->
      <el-col :xs="24" :sm="8">
        <el-card class="metric-card cost-card">
          <div class="metric-header">
            <el-icon class="metric-icon"><Money /></el-icon>
            <span class="metric-title">广告花费</span>
          </div>
          <div class="metric-value">¥{{ formatNumber(metrics.totalCost) }}</div>
          <div class="metric-footer">
            <span :class="trendClass(costTrend)">
              {{ costTrend >= 0 ? '↑' : '↓' }} {{ Math.abs(costTrend).toFixed(1) }}%
            </span>
            <span class="compare-label">较昨日</span>
          </div>
        </el-card>
      </el-col>

      <!-- 销售额指标 -->
      <el-col :xs="24" :sm="8">
        <el-card class="metric-card sales-card">
          <div class="metric-header">
            <el-icon class="metric-icon"><ShoppingCart /></el-icon>
            <span class="metric-title">广告销售</span>
          </div>
          <div class="metric-value">¥{{ formatNumber(metrics.totalSales) }}</div>
          <div class="metric-footer">
            <span :class="trendClass(salesTrend)">
              {{ salesTrend >= 0 ? '↑' : '↓' }} {{ Math.abs(salesTrend).toFixed(1) }}%
            </span>
            <span class="compare-label">较昨日</span>
          </div>
        </el-card>
      </el-col>

      <!-- ACOS指标 -->
      <el-col :xs="24" :sm="8">
        <el-card class="metric-card" :class="acosClass">
          <div class="metric-header">
            <el-icon class="metric-icon"><TrendCharts /></el-icon>
            <span class="metric-title">平均ACOS</span>
          </div>
          <div class="metric-value">{{ (metrics.avgAcos * 100).toFixed(2) }}%</div>
          <div class="metric-footer">
            <el-tag :type="acosTagType" size="small">{{ acosLabel }}</el-tag>
            <span class="compare-label">目标 &lt; 20%</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 次级指标 -->
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :xs="12" :sm="6">
        <div class="sub-metric">
          <div class="sub-label">总订单</div>
          <div class="sub-value">{{ metrics.totalOrders }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="sub-metric">
          <div class="sub-label">平均ROAS</div>
          <div class="sub-value">{{ metrics.avgRoas?.toFixed(2) || '-' }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="sub-metric">
          <div class="sub-label">平均CPC</div>
          <div class="sub-value">¥{{ metrics.avgCpc?.toFixed(2) || '-' }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="sub-metric">
          <div class="sub-label">转化率</div>
          <div class="sub-value">{{ (metrics.conversionRate * 100).toFixed(2) }}%</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Money, ShoppingCart, TrendCharts } from '@element-plus/icons-vue'

const props = defineProps({
  metrics: {
    type: Object,
    default: () => ({
      totalCost: 0,
      totalSales: 0,
      totalOrders: 0,
      avgAcos: 0,
      avgRoas: 0,
      avgCpc: 0,
      conversionRate: 0
    })
  },
  costTrend: {
    type: Number,
    default: 0
  },
  salesTrend: {
    type: Number,
    default: 0
  }
})

const acosClass = computed(() => {
  const acos = props.metrics.avgAcos || 0
  if (acos < 0.15) return 'acos-good'
  if (acos < 0.25) return 'acos-warning'
  return 'acos-danger'
})

const acosTagType = computed(() => {
  const acos = props.metrics.avgAcos || 0
  if (acos < 0.15) return 'success'
  if (acos < 0.25) return 'warning'
  return 'danger'
})

const acosLabel = computed(() => {
  const acos = props.metrics.avgAcos || 0
  if (acos < 0.15) return '优秀'
  if (acos < 0.25) return '良好'
  return '需优化'
})

function formatNumber(num) {
  if (!num) return '0'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function trendClass(trend) {
  return trend >= 0 ? 'trend-up' : 'trend-down'
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



.core-metrics {
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
  padding: 10px;
}

.metric-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.metric-icon {
  font-size: 20px;
  color: #8b5cf6;
}

.metric-title {
  font-size: 14px;
  color: #909399;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.metric-footer {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.trend-up {
  color: #67c23a;
  font-weight: 600;
}

.trend-down {
  color: #f56c6c;
  font-weight: 600;
}

.compare-label {
  color: #c0c4cc;
}

/* ACOS状态 */
.acos-good {
  border-left: 3px solid #67c23a;
}

.acos-warning {
  border-left: 3px solid #e6a23c;
}

.acos-danger {
  border-left: 3px solid #f56c6c;
}

.cost-card .metric-icon {
  color: #e6a23c;
}

.sales-card .metric-icon {
  color: #67c23a;
}

/* 次级指标 */
.sub-metric {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.sub-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.sub-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
</style>
