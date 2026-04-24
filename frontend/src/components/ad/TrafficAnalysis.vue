<template>
  <div class="traffic-analysis minimal-white">
    <el-row :gutter="16">
      <!-- 展示与点击 -->
      <el-col :xs="24" :sm="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><View /></el-icon>
              <span>流量指标</span>
            </div>
          </template>
          <div class="traffic-stats">
            <div class="traffic-item">
              <div class="traffic-label">总展示 (Impressions)</div>
              <div class="traffic-value">{{ formatNumber(traffic.impressions) }}</div>
            </div>
            <div class="traffic-item">
              <div class="traffic-label">总点击 (Clicks)</div>
              <div class="traffic-value">{{ formatNumber(traffic.clicks) }}</div>
            </div>
            <el-divider />
            <div class="traffic-item highlight">
              <div class="traffic-label">点击率 (CTR)</div>
              <div class="traffic-value" :class="ctrClass">{{ (traffic.ctr * 100).toFixed(2) }}%</div>
              <div class="traffic-hint">行业平均 2-3%</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 转化分析 -->
      <el-col :xs="24" :sm="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <el-icon><CircleCheck /></el-icon>
              <span>转化分析</span>
            </div>
          </template>
          <div class="traffic-stats">
            <div class="traffic-item">
              <div class="traffic-label">转化订单数</div>
              <div class="traffic-value">{{ metrics.totalOrders }}</div>
            </div>
            <div class="traffic-item">
              <div class="traffic-label">客单价</div>
              <div class="traffic-value">¥{{ avgOrderValue }}</div>
            </div>
            <el-divider />
            <div class="traffic-item highlight">
              <div class="traffic-label">转化率 (CVR)</div>
              <div class="traffic-value" :class="cvrClass">{{ (metrics.conversionRate * 100).toFixed(2) }}%</div>
              <div class="traffic-hint">点击到订单的转化比例</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { View, CircleCheck } from '@element-plus/icons-vue'

const props = defineProps({
  traffic: {
    type: Object,
    default: () => ({
      impressions: 0,
      clicks: 0,
      ctr: 0
    })
  },
  metrics: {
    type: Object,
    default: () => ({
      totalOrders: 0,
      totalSales: 0,
      conversionRate: 0
    })
  }
})

const avgOrderValue = computed(() => {
  if (!props.metrics.totalOrders) return '0.00'
  return (props.metrics.totalSales / props.metrics.totalOrders).toFixed(2)
})

const ctrClass = computed(() => {
  const ctr = props.traffic.ctr || 0
  if (ctr >= 0.03) return 'excellent'
  if (ctr >= 0.02) return 'good'
  return 'warning'
})

const cvrClass = computed(() => {
  const cvr = props.metrics.conversionRate || 0
  if (cvr >= 0.05) return 'excellent'
  if (cvr >= 0.03) return 'good'
  return 'warning'
})

function formatNumber(num) {
  if (!num) return '0'
  return num.toLocaleString('zh-CN')
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



.traffic-analysis {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.card-header .el-icon {
  color: #8b5cf6;
}

.traffic-stats {
  padding: 10px 0;
}

.traffic-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.traffic-item:last-child {
  margin-bottom: 0;
}

.traffic-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.traffic-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.traffic-value.excellent {
  color: #67c23a;
}

.traffic-value.good {
  color: #8b5cf6;
}

.traffic-value.warning {
  color: #e6a23c;
}

.traffic-hint {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}

.traffic-item.highlight {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 8px;
  padding: 12px;
  margin: 0 -4px;
}

.traffic-item.highlight .traffic-value {
  font-size: 32px;
}
</style>
