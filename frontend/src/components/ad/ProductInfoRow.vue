<template>
  <el-card class="product-info-row" shadow="hover" :body-style="{ padding: '0 20px', height: '60px' }">
    <el-row :gutter="40" class="info-row" align="middle">
      <!-- 产品名称 -->
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-item info-name">
          <div class="info-label">产品名称</div>
          <div class="info-value product-name" :title="product?.name">
            {{ product?.name || '-' }}
            <el-badge v-if="logCount > 0" :value="logCount" class="log-badge-inline" />
          </div>
        </div>
      </el-col>
      
      <!-- SKU -->
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-item info-sku">
          <div class="info-label">SKU</div>
          <div class="info-value" :title="product?.sku">
            {{ product?.sku || '-' }}
          </div>
        </div>
      </el-col>
      
      <!-- 店铺 -->
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-item info-shop">
          <div class="info-label">店铺</div>
          <div class="info-value" :title="shop?.name">
            {{ shop?.name || '-' }}
          </div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  product: {
    type: Object,
    default: () => ({
      name: '',
      product_id: '',
      sku: ''
    })
  },
  shop: {
    type: Object,
    default: () => ({
      name: ''
    })
  },
  startDate: {
    type: String,
    default: ''
  },
  endDate: {
    type: String,
    default: ''
  }
})

const logCount = ref(0)

async function fetchLogCount() {
  if (!props.product?.product_id) {
    logCount.value = 0
    return
  }
  
  try {
    const params = new URLSearchParams()
    params.append('product_ids', props.product.product_id)
    if (props.startDate) params.append('start_date', props.startDate)
    if (props.endDate) params.append('end_date', props.endDate)
    
    const response = await axios.get('/api/operation-logs/counts?' + params.toString())
    logCount.value = response.data[props.product.product_id] || 0
  } catch (error) {
    console.error('获取日志数量失败', error)
    logCount.value = 0
  }
}

watch(() => props.product?.product_id, fetchLogCount)
watch(() => props.startDate, fetchLogCount)
watch(() => props.endDate, fetchLogCount)

onMounted(fetchLogCount)
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



.product-info-row {
  margin-bottom: 16px;
  border-radius: 8px;
  height: 60px;
  overflow: hidden;
}

.info-row {
  height: 60px;
}

.info-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 60px;
  padding: 0 12px;
  border-left: 3px solid;
}

/* 产品名称 - 绿色 */
.info-name {
  border-left-color: #67c23a;
  background: linear-gradient(90deg, rgba(103, 194, 58, 0.05) 0%, transparent 100%);
}

/* SKU - 紫色 */
.info-sku {
  border-left-color: #8b5cf6;
  background: linear-gradient(90deg, rgba(139, 92, 246, 0.05) 0%, transparent 100%);
}

/* 店铺 - 橙色 */
.info-shop {
  border-left-color: #e6a23c;
  background: linear-gradient(90deg, rgba(230, 162, 60, 0.05) 0%, transparent 100%);
}

.info-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
  line-height: 1;
}

.info-value {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.3;
}

.product-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}

.log-badge-inline {
  flex-shrink: 0;
}

.log-badge-inline :deep(.el-badge__content) {
  background: #8b5cf6;
  border: none;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .product-info-row {
    height: auto;
  }
  
  .product-info-row :deep(.el-card__body) {
    height: auto !important;
    padding: 12px 16px !important;
  }
  
  .info-row {
    height: auto;
  }
  
  .info-item {
    height: auto;
    padding: 10px 12px;
    margin-bottom: 8px;
    border-radius: 4px;
  }
  
  .info-item:last-child {
    margin-bottom: 0;
  }
  
  .info-label {
    font-size: 12px;
  }
  
  .info-value {
    font-size: 14px;
  }
  
  .product-name {
    font-size: 15px;
  }
}
</style>
