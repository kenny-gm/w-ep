<template>
  <el-card class="optimization-advice">
    <template #header>
      <div class="card-header minimal-white">
        <div class="header-left">
          <el-icon><Cpu /></el-icon>
          <span class="header-title">AI优化建议</span>
          <el-tag size="small" type="info">智能分析</el-tag>
        </div>
        <el-button size="small" :loading="refreshing" @click="refreshAdvice">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </template>

    <div v-if="advice.length === 0" class="empty-state">
      <el-empty description="暂无优化建议">
        <el-button type="primary" size="small" @click="refreshAdvice">生成建议</el-button>
      </el-empty>
    </div>

    <div v-else class="advice-list">
      <div
        v-for="(item, index) in advice"
        :key="index"
        class="advice-item"
        :class="`advice-${item.type}`"
      >
        <div class="advice-header">
          <div class="advice-icon" :class="`icon-${item.level}`">
            <el-icon v-if="item.level === 'danger'"><WarningFilled /></el-icon>
            <el-icon v-else-if="item.level === 'warning'"><Warning /></el-icon>
            <el-icon v-else-if="item.level === 'success'"><CircleCheckFilled /></el-icon>
            <el-icon v-else><InfoFilled /></el-icon>
          </div>
          <div class="advice-title">
            <el-tag :type="getTagType(item.level)" size="small">{{ item.title }}</el-tag>
            <span class="product-name" v-if="item.product">【{{ item.product }}】</span>
          </div>
        </div>
        <div class="advice-content">
          {{ item.content }}
        </div>
      </div>
    </div>

    <!-- 建议统计 -->
    <div v-if="advice.length > 0" class="advice-stats">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="stat-item">
            <span class="stat-dot danger"></span>
            <span class="stat-label">紧急</span>
            <span class="stat-count">{{ dangerCount }}</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="stat-dot warning"></span>
            <span class="stat-label">警告</span>
            <span class="stat-count">{{ warningCount }}</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="stat-dot info"></span>
            <span class="stat-label">建议</span>
            <span class="stat-count">{{ infoCount }}</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="stat-dot success"></span>
            <span class="stat-label">优秀</span>
            <span class="stat-count">{{ successCount }}</span>
          </div>
        </el-col>
      </el-row>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  Cpu, Refresh, WarningFilled, Warning, CircleCheckFilled, InfoFilled 
} from '@element-plus/icons-vue'

const props = defineProps({
  advice: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['refresh'])

const refreshing = ref(false)

const dangerCount = computed(() => props.advice.filter(a => a.level === 'danger').length)
const warningCount = computed(() => props.advice.filter(a => a.level === 'warning').length)
const infoCount = computed(() => props.advice.filter(a => a.level === 'info').length)
const successCount = computed(() => props.advice.filter(a => a.level === 'success').length)

function getTagType(level) {
  const map = {
    danger: 'danger',
    warning: 'warning',
    info: 'info',
    success: 'success'
  }
  return map[level] || 'info'
}

function refreshAdvice() {
  refreshing.value = true
  emit('refresh')
  setTimeout(() => {
    refreshing.value = false
  }, 1000)
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



.optimization-advice {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.header-left .el-icon {
  color: #8b5cf6;
  font-size: 18px;
}

.empty-state {
  padding: 40px 0;
}

.advice-list {
  max-height: 500px;
  overflow-y: auto;
}

.advice-item {
  padding: 16px;
  margin-bottom: 12px;
  border-radius: 8px;
  border-left: 4px solid;
  background: #fafafa;
}

.advice-item:last-child {
  margin-bottom: 0;
}

.advice-item.advice-acos {
  border-left-color: #f56c6c;
}

.advice-item.advice-ctr {
  border-left-color: #e6a23c;
}

.advice-item.advice-budget {
  border-left-color: #409eff;
}

.advice-item.advice-roas {
  border-left-color: #67c23a;
}

.advice-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.advice-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.advice-icon.icon-danger {
  background: #fef0f0;
  color: #f56c6c;
}

.advice-icon.icon-warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.advice-icon.icon-info {
  background: #ecf5ff;
  color: #409eff;
}

.advice-icon.icon-success {
  background: #f0f9eb;
  color: #67c23a;
}

.advice-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.product-name {
  color: #606266;
}

.advice-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  padding-left: 44px;
}

.advice-stats {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.stat-dot.danger {
  background: #f56c6c;
}

.stat-dot.warning {
  background: #e6a23c;
}

.stat-dot.info {
  background: #409eff;
}

.stat-dot.success {
  background: #67c23a;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.stat-count {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

@media (max-width: 768px) {
  .advice-stats .el-row {
    flex-wrap: wrap;
  }
  
  .advice-stats .el-col {
    margin-bottom: 12px;
  }
}
</style>
