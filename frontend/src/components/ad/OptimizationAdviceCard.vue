<template>
  <el-card class="advice-card" shadow="hover">
    <template #header>
      <div class="card-header minimal-white">
        <span class="card-title">🤖 AI优化建议</span>
        <el-tag size="small" type="info">智能分析</el-tag>
      </div>
    </template>

    <!-- 整体表现 -->
    <div class="advice-overall">
      <div class="overall-header">📊 整体表现</div>
      <p class="overall-content">{{ advice.overall }}</p>
    </div>

    <!-- 各广告类型建议 -->
    <el-collapse v-if="advice.by_type" class="advice-collapse">
      <el-collapse-item title="🔍 CPM搜索建议" name="cpm_search">
        <div class="advice-detail" v-html="formatAdvice(advice.by_type.cpm_search)"></div>
      </el-collapse-item>
      <el-collapse-item title="📱 CPM推荐建议" name="cpm_recommend">
        <div class="advice-detail" v-html="formatAdvice(advice.by_type.cpm_recommend)"></div>
      </el-collapse-item>
      <el-collapse-item title="💰 CPC搜索建议" name="cpc_search">
        <div class="advice-detail" v-html="formatAdvice(advice.by_type.cpc_search)"></div>
      </el-collapse-item>
    </el-collapse>

    <!-- 预算分配建议 -->
    <div class="budget-allocation" v-if="advice.budget_allocation">
      <div class="budget-header">💡 预算分配建议</div>
      <p class="budget-content">{{ advice.budget_allocation }}</p>
    </div>
  </el-card>
</template>

<script setup>
const props = defineProps({
  advice: {
    type: Object,
    default: () => ({
      overall: '',
      by_type: {},
      budget_allocation: ''
    })
  }
})

function formatAdvice(text) {
  if (!text) return ''
  return text.replace(/\n/g, '<br>')
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



.advice-card {
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

.advice-overall {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.overall-header {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
  opacity: 0.9;
}

.overall-content {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
}

.advice-collapse {
  margin-bottom: 16px;
}

.advice-detail {
  padding: 8px 0;
  line-height: 1.8;
  font-size: 13px;
}

.budget-allocation {
  background: #f0f9eb;
  border-left: 4px solid #67c23a;
  padding: 12px 16px;
  border-radius: 4px;
}

.budget-header {
  font-weight: 600;
  color: #67c23a;
  margin-bottom: 8px;
  font-size: 14px;
}

.budget-content {
  margin: 0;
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}
</style>
