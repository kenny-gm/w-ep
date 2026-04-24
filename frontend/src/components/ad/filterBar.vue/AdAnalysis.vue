<template>
  <div class="ad-analysis">
    <!-- 筛选栏 -->
    <FilterBar 
      v-model:shop="selectedShop"
      v-model:product="selectedProduct"
      v-model:time-range="timeRange"
      @change="handleFilterChange"
    />
    
    <!-- 产品详情卡片 -->
    <ProductDetailCard 
      :product="currentProduct" 
      :shop="currentShop" 
    />
    
    <!-- 第一行：核心指标 7列 -->
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
      <el-button @click="openAlertSettings">
        <el-icon><Setting /></el-icon>
        预警设置
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download, DataAnalysis, Setting } from '@element-plus/icons-vue'

// 导入组件
import FilterBar from '../components/ad/FilterBar.vue'
import ProductDetailCard from '../components/ad/ProductDetailCard.vue'
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

// 筛选状态
const selectedShop = ref(null)
const selectedProduct = ref(null)
const timeRange = ref('7days')
const activeAdType = ref('all')

// 数据状态
const shops = ref(mockShops)
const products = ref(mockProducts)
const coreMetrics = ref(mockCoreMetrics)
const salesTrend = ref(mockSalesTrend)
const adMetrics = ref(mockAdMetrics)
const trafficSource = ref(mockTrafficSource)
const trafficTrend = ref(mockTrafficTrend)
const adCampaigns = ref(mockAdCampaigns)
const keywordsData = ref(mockKeywords)
const optimizationAdvice = ref(mockOptimizationAdvice)

// 计算当前选中的产品和店铺
const currentProduct = computed(() => {
  if (!selectedProduct.value) return mockProducts[0]
  return products.value.find(p => p.id === selectedProduct.value) || mockProducts[0]
})

const currentShop = computed(() => {
  if (!selectedShop.value) return mockShops[0]
  return shops.value.find(s => s.id === selectedShop.value) || mockShops[0]
})

// 筛选变化处理
const handleFilterChange = () => {
  console.log('筛选条件变化:', { 
    selectedShop: selectedShop.value, 
    selectedProduct: selectedProduct.value, 
    timeRange: timeRange.value 
  })
  loadData()
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

// 设置预警
const openAlertSettings = () => {
  ElMessage.info('预警设置功能开发中...')
}

onMounted(() => {
  // 初始化默认选中
  selectedShop.value = mockShops[0]?.id
  selectedProduct.value = mockProducts[0]?.id
  loadData()
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
