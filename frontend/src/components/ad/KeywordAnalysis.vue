<template>
  <el-card class="keyword-card" shadow="hover">
    <template #header>
      <div class="card-header minimal-white">
        <span class="card-title">🔑 关键词分析</span>
        <el-tag size="small" type="info" effect="plain">{{ adType === 'cpc' ? 'CPC搜索' : 'CPM搜索' }}</el-tag>
      </div>
    </template>

    <el-table :data="keywords" stripe border size="small">
      <el-table-column prop="keyword" label="关键词" width="120">
        <template #default="{ row }">
          <el-tag size="small" type="info">{{ row.keyword }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="impressions" label="展示" width="80" sortable>
        <template #default="{ row }">{{ formatNumber(row.impressions) }}</template>
      </el-table-column>
      <el-table-column prop="clicks" label="点击" width="70" sortable />
      <el-table-column prop="ctr" label="CTR" width="75" sortable>
        <template #default="{ row }">{{ (row.ctr * 100).toFixed(2) }}%</template>
      </el-table-column>
      <el-table-column prop="spend" label="花费" width="80" sortable>
        <template #default="{ row }">₽{{ row.spend }}</template>
      </el-table-column>
      <el-table-column prop="sales" label="销售额" width="90" sortable>
        <template #default="{ row }">₽{{ formatNumber(row.sales) }}</template>
      </el-table-column>
      <el-table-column prop="roas" label="ROAS" width="70" sortable>
        <template #default="{ row }">
          <span :class="getRoasClass(row.roas)">{{ row.roas.toFixed(1) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="cpc" label="CPC" width="65">
        <template #default="{ row }">₽{{ row.cpc }}</template>
      </el-table-column>
      <el-table-column prop="position" label="排名" width="65" sortable>
        <template #default="{ row }">{{ row.position?.toFixed(1) || '-' }}</template>
      </el-table-column>
      <el-table-column label="优化建议" min-width="180">
        <template #default="{ row }">
          <span :class="getSuggestionClass(row.suggestion_type)">{{ row.suggestion }}</span>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { formatNumber } from '../../utils/currency'

const props = defineProps({
  keywords: {
    type: Array,
    default: () => []
  },
  adType: {
    type: String,
    default: 'cpm'
  }
})

function getRoasClass(roas) {
  if (roas >= 3) return 'metric-good'
  if (roas >= 2) return 'metric-neutral'
  return 'metric-warning'
}

function getSuggestionClass(type) {
  const map = {
    increase: 'suggestion-increase',
    maintain: 'suggestion-maintain',
    optimize: 'suggestion-optimize',
    pause: 'suggestion-pause'
  }
  return map[type] || ''
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



.keyword-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
}

.metric-good {
  color: #67c23a;
  font-weight: 600;
}

.metric-neutral {
  color: #8b5cf6;
  font-weight: 600;
}

.metric-warning {
  color: #e6a23c;
  font-weight: 600;
}

.suggestion-increase {
  color: #67c23a;
  font-size: 13px;
}

.suggestion-maintain {
  color: #909399;
  font-size: 13px;
}

.suggestion-optimize {
  color: #e6a23c;
  font-size: 13px;
}

.suggestion-pause {
  color: #f56c6c;
  font-size: 13px;
}
</style>
