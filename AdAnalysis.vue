<template>
  <div class="ad-analysis">
    <!-- 筛选栏 -->
    <FilterBar 
      v-model:shop="selectedShop"
      v-model:product="selectedProduct"
      v-model:time-range="timeRange"
      @change="handleFilterChange"
    />
    
    <!-- 产品信息行 -->
    <ProductInfoRow 
      :product="currentProduct" 
      :shop="currentShop" 
    />
    
    <!-- 第一行：核心指标 8列 -->
    <CoreMetricsCard 
      :data="coreMetrics" 
      :ad-data="adMetrics" 
    />
    
    <!-- 第二行：图表三栏 -->
    <el-row :gutter="16" class="charts-row">
      <el-col :xs="24" :lg="8">
        <TrafficSourceChart :data="trafficSource" />
      </el-col>
      <el-col :xs="24" :lg="8">
        <SalesTrendChart :data="salesTrend" />
      </el-col>
      <el-col :xs="24" :lg="8">
        <TrafficTrendChart :data="trafficTrend" />
      </el-col>
    </el-row>
    
    <!-- 第三行：广告活动数据表格 -->
    <AdDataTable 
      :data="adCampaigns"
      :active-type="activeAdType"
      @tab-change="activeAdType = $event"
    />
    
    <!-- 第四行：关键词分析（仅CPM搜索时显示） -->
    <KeywordAnalysis 
      v-if="activeAdType === 'cpm_search' || activeAdType === 'all'"
      :keywords="keywordsData"
    />
    
    <!-- 第五行：AI优化建议卡片 -->
    <OptimizationAdviceCard :advice="optimizationAdvice" />
    
    <!-- 第六行：快捷操作按钮 -->
    <div class="quick-actions">
      <el-button type="primary" @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
      <el-button @click="exportReport">
        <el-icon><Download /></el-icon>
        导出报表
      </el-button>
      <el-button @click="viewDetailReport">
        <el-icon><DataAnalysis /></el-icon>
        详细报告
      </el-button>
      <!-- 预警设置按钮 - 仅管理员可见 -->
      <el-button v-if="isAdmin" type="warning" @click="openAlertSettings">
        <el-icon><Setting /></el-icon>
        预警设置
      </el-button>
    </div>
    
    <!-- 预警设置弹窗 -->
    <el-dialog 
      v-model="alertSettingsVisible" 
      title="📊 指标预警设置"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-table :data="thresholds" v-loading="loadingThresholds" stripe size="small">
        <el-table-column prop="display_name" label="指标名称" width="120" />
        
        <el-table-column label="警告阈值" width="110">
          <template #default="{ row }">
            <el-input-number 
              v-model="row.warning_threshold" 
              :min="0" 
              :max="row.metric_name === 'acos' ? 1 : 100"
              :precision="2"
              size="small"
              :step="row.metric_name === 'acos' ? 0.01 : 0.1"
              @change="handleThresholdChange(row)"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="危险阈值" width="110">
          <template #default="{ row }">
            <el-input-number 
              v-model="row.danger_threshold" 
              :min="0"
              :max="row.metric_name === 'acos' ? 1 : 100"
              :precision="2"
              size="small"
              :step="row.metric_name === 'acos' ? 0.01 : 0.1"
              @change="handleThresholdChange(row)"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="comparison" label="比较方式" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.comparison === 'less_than' ? 'success' : 'danger'">
              {{ row.comparison === 'less_than' ? '小于' : '大于' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="颜色" width="150">
          <template #default="{ row }">
            <div class="color-pickers">
              <el-tooltip content="正常" placement="top">
                <el-color-picker v-model="row.good_color" size="small" @change="handleThresholdChange(row)" />
              </el-tooltip>
              <el-tooltip content="警告" placement="top">
                <el-color-picker v-model="row.warning_color" size="small" @change="handleThresholdChange(row)" />
              </el-tooltip>
              <el-tooltip content="危险" placement="top">
                <el-color-picker v-model="row.danger_color" size="small" @change="handleThresholdChange(row)" />
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 说明 -->
      <div class="threshold-help">
        <el-alert type="info" :closable="false">
          <template #title>
            <span style="font-weight: 600">预警规则说明</span>
          </template>
          <ul class="help-list">
            <li><strong>ROAS &lt; {{ getThresholdDisplay('roas', 'warning') }}</strong>：显示警告颜色</li>
            <li><strong>ACOS &gt; {{ getThresholdDisplay('acos', 'warning') }}%</strong>：显示警告颜色</li>
            <li><strong>CTR &lt; {{ getThresholdDisplay('ctr', 'warning') }}%</strong>：显示警告颜色</li>
            <li><strong>自然订单占比 &lt; {{ getThresholdDisplay('natural_orders_ratio', 'warning') }}%</strong>：显示警告颜色</li>
          </ul>
        </el-alert>
      </div>
      
      <template #footer>
        <el-button @click="alertSettingsVisible = false">关闭</el-button>
        <el-button type="primary" @click="saveAllThresholds" :loading="saving">保存设置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download, DataAnalysis, Setting } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

// 导入组件
import FilterBar from '../components/ad/FilterBar.vue'
import ProductInfoRow from '../components/ad/ProductInfoRow.vue'
import CoreMetricsCard from '../components/ad/CoreMetricsCard.vue'
import SalesTrendChart from '../components/ad/SalesTrendChart.vue'
import TrafficSourceChart from '../components/ad/TrafficSourceChart.vue'
import TrafficTrendChart from '../components/ad/TrafficTrendChart.vue'
import AdDataTable from '../components/ad/AdDataTable.vue'
import KeywordAnalysis from '../components/ad/KeywordAnalysis.vue'
import OptimizationAdviceCard from '../components/ad/OptimizationAdviceCard.vue'

// 导入Mock数据
import { 
  mockShops, 
  mockProducts, 
  mockCoreMetrics, 
  mockSalesTrend,
  mockAdMetrics,
  mockTrafficSource,
  mockTrafficTrend,
  mockAdCampaigns,
  mockKeywords,
  mockOptimizationAdvice
} from '../components/ad/mockData'

// Auth store
const authStore = useAuthStore()

// 是否为管理员
const isAdmin = computed(() => authStore.user?.role === 'admin')

// 预警设置状态
const alertSettingsVisible = ref(false)
const thresholds = ref([])
const loadingThresholds = ref(false)
const saving = ref(false)
const changedThresholds = ref(new Set())

// 筛选状态
const selectedShop = ref(null)
const selectedProduct = ref(null)
const timeRange = ref('7days')
const activeAdType = ref('all')

// 数据状态 - 使用空数组而不是mock数据
const shops = ref([])
const products = ref([])
const coreMetrics = ref({})
const salesTrend = ref([])
const adMetrics = ref({})
const trafficSource = ref({
  natural_ratio: 0,
  ad_ratio: 0,
  other_ratio: 0,
  natural_visitors: 0,
  ad_visitors: 0,
  other_visitors: 0,
  total_visitors: 0
})
const trafficTrend = ref([])
const adCampaigns = ref([])
const keywordsData = ref([])
const optimizationAdvice = ref([])
const loading = ref(false)

// 计算当前选中的产品和店铺
const currentProduct = computed(() => {
  if (!selectedProduct.value || products.value.length === 0) return null
  return products.value.find(p => p.id === selectedProduct.value) || null
})

const currentShop = computed(() => {
  if (!selectedShop.value || shops.value.length === 0) return null
  return shops.value.find(s => s.id === selectedShop.value) || null
})

// 加载店铺列表
async function fetchShops() {
  try {
    const response = await axios.get('/api/shops/')
    shops.value = response.data
    if (shops.value.length > 0 && !selectedShop.value) {
      selectedShop.value = shops.value[0].id
    }
  } catch (error) {
    console.error('获取店铺列表失败', error)
  }
}

// 加载店铺产品列表
async function fetchProducts(shopId) {
  if (!shopId) {
    products.value = []
    return
  }
  try {
    const response = await axios.get(`/api/shops/${shopId}/products/`)
    products.value = response.data
    if (products.value.length > 0 && !selectedProduct.value) {
      selectedProduct.value = products.value[0].id
    }
  } catch (error) {
    console.error('获取产品列表失败', error)
  }
}

// 加载产品广告数据
async function fetchAdData() {
  if (!selectedProduct.value) return
  
  loading.value = true
  try {
    const dateFrom = getDateFrom(timeRange.value)
    const response = await axios.get(`/api/products/${selectedProduct.value}/ads/`, {
      params: {
        date_from: dateFrom,
        date_to: new Date().toISOString().split('T')[0]
      }
    })
    
    const data = response.data
    console.log('API响应数据:', data)
    
    // 更新数据
    console.log('设置adMetrics:', data.summary)
    const summary = data.summary || {}
    adMetrics.value = summary
    
    // 同时设置coreMetrics用于显示（将广告数据映射到核心指标）
    coreMetrics.value = {
      total_sales: summary.sales || 0,
      total_sales_trend: 0,
      total_orders: summary.orders || 0,
      total_orders_trend: 0,
      natural_orders_ratio: 0,
      natural_orders_ratio_trend: 0
    }
    
    adCampaigns.value = data.adverts || []
    
    // 获取流量来源分析数据
    try {
      const trafficResponse = await axios.get(`/api/shops/${selectedShop.value}/traffic-source/`, {
        params: {
          date_from: dateFrom,
          date_to: new Date().toISOString().split('T')[0]
        }
      })
      trafficSource.value = trafficResponse.data
    } catch (trafficError) {
      console.error('获取流量来源数据失败', trafficError)
    }
    
    // 生成每日趋势数据
    if (data.daily_data && data.daily_data.length > 0) {
      salesTrend.value = data.daily_data.map(d => ({
        date: d.date,
        sales: d.sales || 0,
        orders: d.orders || 0
      }))
      trafficTrend.value = data.daily_data.map(d => ({
        date: d.date,
        impressions: d.impressions || 0,
        clicks: d.clicks || 0
      }))
    } else {
      // 生成模拟的每日趋势数据
      generateMockDailyData(dateFrom)
    }
    
  } catch (error) {
    console.error('获取广告数据失败', error)
    // 使用模拟数据
    generateMockDailyData(getDateFrom(timeRange.value))
  } finally {
    loading.value = false
  }
}

// 根据时间范围获取开始日期
function getDateFrom(timeRange) {
  const now = new Date()
  let days = 7
  if (timeRange === 'yesterday') days = 1
  else if (timeRange === '30days') days = 30
  else if (timeRange === '90days') days = 90
  else if (timeRange === '7days') days = 7
  
  const date = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)
  return date.toISOString().split('T')[0]
}

// 生成模拟每日数据
function generateMockDailyData(dateFrom) {
  const days = Math.ceil((new Date() - new Date(dateFrom)) / (1000 * 60 * 60 * 24))
  const dailyData = []
  
  for (let i = 0; i < days; i++) {
    const date = new Date(new Date(dateFrom).getTime() + i * 24 * 60 * 60 * 1000)
    dailyData.push({
      date: date.toISOString().split('T')[0],
      impressions: Math.floor(Math.random() * 10000),
      clicks: Math.floor(Math.random() * 500),
      spend: Math.floor(Math.random() * 5000),
      sales: Math.floor(Math.random() * 15000),
      orders: Math.floor(Math.random() * 50)
    })
  }
  
  salesTrend.value = dailyData.map(d => ({ date: d.date, sales: d.sales, orders: d.orders }))
  trafficTrend.value = dailyData.map(d => ({ date: d.date, impressions: d.impressions, clicks: d.clicks }))
  // 只有在没有真实数据时才使用模拟数据
  if (!trafficSource.value.total_visitors) {
    trafficSource.value = {
      ad_ratio: 25,
      natural_ratio: 73,
      other_ratio: 2,
      ad_visitors: 2500,
      natural_visitors: 7300,
      other_visitors: 200,
      total_visitors: 10000
    }
  }
  adCampaigns.value = [
    { id: 1, name: '智能投放', status: 'active', type: 'cpm_search', impressions: 50000, clicks: 1000, spend: 5000, sales: 15000 },
    { id: 2, name: '爆款推广', status: 'active', type: 'cpm_recommend', impressions: 30000, clicks: 600, spend: 3000, sales: 9000 },
    { id: 3, name: '长尾词', status: 'active', type: 'cpc_search', impressions: 20000, clicks: 400, spend: 2000, sales: 6000 }
  ]
  keywordsData.value = [
    { keyword: '羊毛大衣', impressions: 25000, clicks: 800, ctr: 0.032, spend: 2500, sales: 7500 },
    { keyword: '女士大衣', impressions: 18000, clicks: 540, ctr: 0.03, spend: 1800, sales: 5400 },
    { keyword: '冬季外套', impressions: 12000, clicks: 360, ctr: 0.03, spend: 1200, sales: 3600 }
  ]
  optimizationAdvice.value = [
    { type: 'info', message: '搜索广告CTR高于类目广告，建议增加预算' },
    { type: 'warning', message: '部分关键词ACOS过高，建议优化出价' },
    { type: 'success', message: '整体ROAS为2.8，处于健康水平' }
  ]
}

// 筛选变化处理
const handleFilterChange = () => {
  console.log('筛选条件变化:', { 
    selectedShop: selectedShop.value, 
    selectedProduct: selectedProduct.value, 
    timeRange: timeRange.value 
  })
  
  // 当店铺变化时，重新加载产品列表
  if (selectedShop.value) {
    fetchProducts(selectedShop.value)
  }
  
  // 加载广告数据（只调用API获取真实数据，不使用mock覆盖）
  fetchAdData()
}

// 加载数据
const loadData = () => {
  // 使用Mock数据
  coreMetrics.value = mockCoreMetrics
  salesTrend.value = mockSalesTrend
  adMetrics.value = mockAdMetrics
  trafficSource.value = mockTrafficSource
  trafficTrend.value = mockTrafficTrend
  adCampaigns.value = mockAdCampaigns
  keywordsData.value = mockKeywords.filter(k => k.impressions > 100) // 过滤展示量>100
  optimizationAdvice.value = mockOptimizationAdvice
}

// 刷新数据
const refreshData = () => {
  ElMessage.success('数据刷新中...')
  loadData()
}

// 导出报表
const exportReport = () => {
  ElMessage.info('导出报表功能开发中...')
}

// 查看详细报告
const viewDetailReport = () => {
  ElMessage.info('详细报告功能开发中...')
}

// 打开预警设置
const openAlertSettings = async () => {
  alertSettingsVisible.value = true
  await loadThresholds()
}

// 加载阈值配置
const loadThresholds = async () => {
  loadingThresholds.value = true
  try {
    const response = await axios.get('/api/metric-thresholds/')
    thresholds.value = response.data
    changedThresholds.value = new Set()
  } catch (error) {
    ElMessage.error('加载阈值配置失败')
  } finally {
    loadingThresholds.value = false
  }
}

// 标记阈值已修改
const handleThresholdChange = (row) => {
  changedThresholds.value.add(row.metric_name)
}

// 获取阈值显示值
const getThresholdDisplay = (metricName, type) => {
  const threshold = thresholds.value.find(t => t.metric_name === metricName)
  if (!threshold) return '-'
  
  const value = type === 'warning' ? threshold.warning_threshold : threshold.danger_threshold
  
  // 根据指标类型格式化显示
  if (metricName === 'acos') {
    return value != null ? (value * 100).toFixed(0) : '-'
  } else if (metricName === 'ctr' || metricName === 'natural_orders_ratio') {
    return value != null ? (value * 100).toFixed(0) : '-'
  } else {
    return value != null ? value.toFixed(1) : '-'
  }
}

// 保存所有阈值
const saveAllThresholds = async () => {
  saving.value = true
  try {
    // 保存所有修改过的阈值
    for (const metricName of changedThresholds.value) {
      const threshold = thresholds.value.find(t => t.metric_name === metricName)
      if (threshold) {
        await axios.put(`/api/metric-thresholds/${metricName}`, {
          display_name: threshold.display_name,
          warning_threshold: threshold.warning_threshold,
          danger_threshold: threshold.danger_threshold,
          good_color: threshold.good_color,
          warning_color: threshold.warning_color,
          danger_color: threshold.danger_color
        })
      }
    }
    
    ElMessage.success('预警设置已保存')
    alertSettingsVisible.value = false
    
    // 刷新页面数据以应用新颜色
    window.location.reload()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  // 加载店铺列表
  fetchShops().then(() => {
    // 如果有选中的店铺，加载产品列表
    if (selectedShop.value) {
      fetchProducts(selectedShop.value)
    }
    // 加载广告数据
    fetchAdData()
  })
})

// 监听产品变化，自动加载广告数据
watch(selectedProduct, (newProductId) => {
  if (newProductId) {
    fetchAdData()
  }
})

// 监听时间范围变化
watch(timeRange, () => {
  if (selectedProduct.value) {
    fetchAdData()
  }
})
</script>

<style scoped>
.ad-analysis {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.charts-row {
  margin-bottom: 20px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 16px;
  background: white;
  border-radius: 12px;
  flex-wrap: wrap;
}

.color-pickers {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.threshold-help {
  margin-top: 16px;
}

.help-list {
  margin: 8px 0 0 0;
  padding-left: 20px;
  line-height: 1.8;
  font-size: 13px;
}

.help-list li {
  margin-bottom: 4px;
}

@media (max-width: 768px) {
  .ad-analysis {
    padding: 12px;
  }
  
  .charts-row .el-col {
    margin-bottom: 16px;
  }
  
  .quick-actions {
    justify-content: center;
  }
}
</style>
