<template>
  <el-card class="product-detail-card">
    <div class="product-header">
      <div class="product-icon">📦</div>
      <div class="product-info">
        <h3 class="product-name">{{ product?.name || '请选择产品' }}</h3>
        <div class="product-meta">
          <el-tag size="small" type="info">ID: {{ product?.product_id || '-' }}</el-tag>
          <el-tag size="small" type="success">{{ shop?.name || '未选择店铺' }}</el-tag>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
const props = defineProps({
  product: {
    type: Object,
    default: null
  },
  shop: {
    type: Object,
    default: null
  }
})
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



.product-detail-card {
  margin-bottom: 20px;
}

.product-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.product-icon {
  font-size: 48px;
}

.product-info {
  flex: 1;
}

.product-name {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.product-meta {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .product-header {
    flex-direction: column;
    text-align: center;
  }
  
  .product-meta {
    justify-content: center;
  }
}
</style>
