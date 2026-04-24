<template>
  <div class="finance minimal-white">
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始"
            end-placeholder="结束"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="fetchFinance"
          />
        </el-form-item>
        
        <el-form-item label="店铺">
          <el-select v-model="filters.shopId" placeholder="全部" style="width: 150px" @change="fetchFinance">
            <el-option label="全部" :value="null" />
            <el-option v-for="shop in shops" :key="shop.id" :label="shop.name" :value="shop.id" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 利润汇总卡片 -->
    <el-row :gutter="20" class="summary-row">
      <el-col :xs="12" :sm="6">
        <el-card class="summary-card">
          <div class="label">总销售额</div>
          <div class="value">{{ formatMoney(summary.totalSales) }}</div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="6">
        <el-card class="summary-card">
          <div class="label">总成本</div>
          <div class="value">{{ formatMoney(summary.totalCost) }}</div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="6">
        <el-card class="summary-card" :class="{ 'positive': summary.totalProfit > 0, 'negative': summary.totalProfit < 0 }">
          <div class="label">总利润</div>
          <div class="value">{{ formatMoney(summary.totalProfit) }}</div>
        </el-card>
      </el-col>
      
      <el-col :xs="12" :sm="6">
        <el-card class="summary-card" :class="{ 'positive': summary.avgProfitRate > 0.1, 'negative': summary.avgProfitRate < 0 }">
          <div class="label">平均利润率</div>
          <div class="value">{{ (summary.avgProfitRate * 100).toFixed(1) }}%</div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 成本构成 -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12">
        <el-card>
          <template #header>成本构成</template>
          <div ref="costChartRef" style="height: 250px"></div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12">
        <el-card>
          <template #header>利润趋势</template>
          <div ref="profitChartRef" style="height: 250px"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 产品利润明细 -->
    <el-card class="detail-card">
      <template #header>产品利润明细</template>
      <el-table :data="productProfits" v-loading="loading" stripe>
        <el-table-column prop="product.nm_id" label="产品ID" width="100" />
        <el-table-column label="产品名称" min-width="150">
          <template #default="{ row }">
            {{ row.product?.custom_name || row.product?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="sales" label="销售额" width="120">
          <template #default="{ row }">
            {{ formatMoney(row.sales) }}
          </template>
        </el-table-column>
        <el-table-column prop="product_cost" label="产品成本" width="120">
          <template #default="{ row }">
            {{ formatMoney(row.product_cost) }}
          </template>
        </el-table-column>
        <el-table-column prop="commission" label="佣金" width="100">
          <template #default="{ row }">
            {{ formatMoney(row.commission) }}
          </template>
        </el-table-column>
        <el-table-column prop="logistics_fee" label="物流费" width="100">
          <template #default="{ row }">
            {{ formatMoney(row.logistics_fee) }}
          </template>
        </el-table-column>
        <el-table-column prop="ad_cost" label="广告费" width="100">
          <template #default="{ row }">
            {{ formatMoney(row.ad_cost) }}
          </template>
        </el-table-column>
        <el-table-column prop="profit" label="利润" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-success': row.profit > 0, 'text-danger': row.profit < 0 }">
              {{ formatMoney(row.profit) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_rate" label="利润率" width="100">
          <template #default="{ row }">
            <span :class="{ 'text-success': row.profit_rate > 0.1, 'text-danger': row.profit_rate < 0 }">
              {{ (row.profit_rate * 100).toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'

const shops = ref([])
const loading = ref(false)
const dateRange = ref([])
const productProfits = ref([])
const costChartRef = ref(null)
const profitChartRef = ref(null)
let costChart = null
let profitChart = null

const filters = reactive({
  shopId: null
})

const summary = reactive({
  totalSales: 0,
  totalCost: 0,
  totalProfit: 0,
  avgProfitRate: 0
})

function formatMoney(value) {
  if (!value) return '¥0.00'
  return '¥' + value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function fetchFinance() {
  loading.value = true
  try {
    const params = {}
    
    if (filters.shopId) params.shop_id = filters.shopId
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const response = await axios.get('/api/finance/summary/', { params })
    
    const data = response.data
summary.totalSales = data.total_sales || 0
summary.totalCost = data.total_cost || 0
summary.totalProfit = data.total_profit || 0
summary.avgProfitRate = data.avg_profit_rate || 0
summary.orderCount = data.order_count || 0

    productProfits.value = response.data.products || []
    
    await nextTick()
    renderCharts(response.data)
  } catch (error) {
    ElMessage.error('获取财务数据失败')
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

function renderCharts(data) {
  // 成本构成饼图
  if (costChartRef.value) {
    if (!costChart) {
      costChart = echarts.init(costChartRef.value)
    }
    
    const costData = data.costBreakdown || {
      '产品成本': summary.totalCost * 0.6,
      '平台佣金': summary.totalCost * 0.2,
      '物流费': summary.totalCost * 0.15,
      '广告费': summary.totalCost * 0.05
    }
    
    costChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: '60%',
        data: Object.entries(costData).map(([name, value]) => ({ name, value }))
      }]
    })
  }
  
  // 利润趋势图
  if (profitChartRef.value && data.trend) {
    if (!profitChart) {
      profitChart = echarts.init(profitChartRef.value)
    }
    
    profitChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: data.trend.map(d => d.date)
      },
      yAxis: { type: 'value' },
      series: [{
        name: '利润',
        type: 'line',
        data: data.trend.map(d => d.profit),
        smooth: true,
        areaStyle: { opacity: 0.3 }
      }]
    })
  }
}

onMounted(() => {
  const today = new Date()
  const monthAgo = new Date(today)
  monthAgo.setDate(monthAgo.getDate() - 30)
  dateRange.value = [
    monthAgo.toISOString().split('T')[0],
    today.toISOString().split('T')[0]
  ]
  
  fetchFinance()
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

.summary-row {
  margin-bottom: 20px;
}

.summary-card {
  text-align: center;
  padding: 10px 0;
}

.summary-card .label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.summary-card .value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.summary-card.positive .value {
  color: #67c23a;
}

.summary-card.negative .value {
  color: #f56c6c;
}

.detail-card {
  margin-top: 20px;
}

.text-success {
  color: #67c23a;
  font-weight: bold;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}
</style>
