<template>
  <div class="orders minimal-white">
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="店铺">
          <el-select v-model="filters.shopId" placeholder="全部" style="width: 150px" @change="fetchOrders">
            <el-option label="全部" :value="null" />
            <el-option v-for="shop in shops" :key="shop.id" :label="shop.name" :value="shop.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="订单状态">
          <el-select v-model="filters.status" placeholder="全部" style="width: 150px" @change="fetchOrders">
            <el-option label="全部" :value="null" />
            <el-option label="待处理" value="new" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="订单日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始"
            end-placeholder="结束"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card>
      <el-table :data="orders" v-loading="loading" stripe>
        <el-table-column prop="order_id" label="订单号" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="订单金额 (₽)" width="140">
          <template #default="{ row }">
            ₽{{ formatMoney(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="commission" label="佣金 (₽)" width="120">
          <template #default="{ row }">
            ₽{{ formatMoney(row.commission) }}
          </template>
        </el-table-column>
        <el-table-column prop="logistics_fee" label="物流费 (₽)" width="120">
          <template #default="{ row }">
            ₽{{ formatMoney(row.logistics_fee) }}
          </template>
        </el-table-column>
        <el-table-column prop="product_cost" label="产品成本 (₽)" width="120">
          <template #default="{ row }">
            ₽{{ row.product_cost?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="profit" label="利润" width="100">
          <template #default="{ row }">
            <span :class="{ 'profit-positive': row.profit > 0, 'profit-negative': row.profit < 0 }">
              ₽{{ row.profit?.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_rate" label="利润率" width="100">
          <template #default="{ row }">
            <span :class="{ 'profit-positive': row.profit_rate > 0.1, 'profit-negative': row.profit_rate < 0 }">
              {{ (row.profit_rate * 100).toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="order_date" label="下单时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.order_date) }}
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchOrders"
        @current-change="fetchOrders"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
// 格式化金额函数已内联

// 格式化金额为卢布
function formatMoney(amount) {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '0'
  }
  return amount.toLocaleString('zh-CN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  })
}
const orders = ref([])
const shops = ref([])
const loading = ref(false)
const dateRange = ref([])

const filters = reactive({
  shopId: null,
  status: null,
  startDate: '',
  endDate: ''
})

const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

function getStatusType(status) {
  const types = {
    'new': 'warning',
    'shipped': 'primary',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = {
    'new': '待处理',
    'shipped': '已发货',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return texts[status] || status
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function handleDateChange(value) {
  if (value) {
    filters.startDate = value[0]
    filters.endDate = value[1]
  } else {
    filters.startDate = ''
    filters.endDate = ''
  }
  fetchOrders()
}

async function fetchOrders() {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.limit,
      limit: pagination.limit
    }
    
    if (filters.shopId) params.shop_id = filters.shopId
    if (filters.status) params.status = filters.status
    if (filters.startDate) params.start_date = filters.startDate
    if (filters.endDate) params.end_date = filters.endDate
    
    const response = await axios.get('/api/orders/', { params })
    orders.value = response.data.items || []
    pagination.total = response.data.total || 0
  } catch (error) {
    ElMessage.error('获取订单失败')
  } finally {
    loading.value = false
  }
}

async function fetchShops() {
  try {
    const response = await axios.get('/api/shops/')
    shops.value = response.data
  } catch (error) {
    console.error('获取店铺失败', error)
  }
}

onMounted(() => {
  fetchOrders()
  fetchShops()
})
</script>

<style scoped>
/* 极简纯白全局样式 */
.minimal-white {
  padding: 16px;
  min-height: 100vh;
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



.filter-card {
  margin-bottom: 20px;
}

.profit-positive {
  color: #67c23a;
  font-weight: bold;
}

.profit-negative {
  color: #f56c6c;
  font-weight: bold;
}
</style>
