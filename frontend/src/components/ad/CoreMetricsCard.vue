<template>
  <el-row :gutter="12" class="metrics-row">
    <!-- 销售额 -->
    <el-col :xs="12" :sm="6" :md="3" :lg="3">
      <el-card class="metric-card sales-card" shadow="hover">
        <div class="metric-label">销售额</div>
        <div class="metric-value">{{ formatRuble(data.sales) }}</div>
      </el-card>
    </el-col>

    <!-- 订单数 -->
    <el-col :xs="12" :sm="6" :md="3" :lg="3">
      <el-card class="metric-card orders-card" shadow="hover">
        <div class="metric-label">订单数</div>
        <div class="metric-value">{{ data.orders || 0 }} 单</div>
      </el-card>
    </el-col>

    <!-- 总访客 -->
    <el-col :xs="12" :sm="6" :md="3" :lg="3">
      <el-card class="metric-card visitors-card" shadow="hover">
        <div class="metric-label">总访客</div>
        <div class="metric-value">{{ formatNumber(data.total_visitors) }}</div>
      </el-card>
    </el-col>

    <!-- 广告访客 -->
    <el-col :xs="12" :sm="6" :md="3" :lg="3">
      <el-card class="metric-card ad-visitors-card" shadow="hover">
        <div class="metric-label">广告访客</div>
        <div class="metric-value">{{ formatNumber(data.ad_visitors) }}</div>
      </el-card>
    </el-col>

    <!-- 广告费 -->
    <el-col :xs="12" :sm="6" :md="3" :lg="3">
      <el-card class="metric-card spend-card" shadow="hover">
        <div class="metric-label">广告费</div>
        <div class="metric-value">{{ formatRuble(data.ad_spend) }}</div>
      </el-card>
    </el-col>

    <!-- 广告点击率 CTR -->
    <el-col :xs="12" :sm="6" :md="3" :lg="3">
      <el-card class="metric-card ctr-card" shadow="hover">
        <div class="metric-label">广告点击率</div>
        <div class="metric-value">{{ ((data.ad_ctr || 0) * 100).toFixed(2) }}%</div>
      </el-card>
    </el-col>

    <!-- 广告加购率 -->
    <el-col :xs="12" :sm="6" :md="3" :lg="3">
      <el-card class="metric-card cart-rate-card" shadow="hover">
        <div class="metric-label">广告加购率</div>
        <div class="metric-value">{{ ((data.ad_cart_rate || 0) * 100).toFixed(2) }}%</div>
      </el-card>
    </el-col>

    <!-- CPC -->
    <el-col :xs="12" :sm="6" :md="3" :lg="3">
      <el-card class="metric-card cpc-card" shadow="hover">
        <div class="metric-label">CPC</div>
        <div class="metric-value">₽ {{ (data.cpc || 0).toFixed(2) }}</div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { computed } from 'vue'
import { formatRuble } from '../../utils/currency'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      sales: 0,
      orders: 0,
      total_visitors: 0,
      ad_visitors: 0,
      ad_spend: 0,
      ad_ctr: 0,
      ad_cart_rate: 0,
      cpc: 0
    })
  },
  // 趋势数据，用于生成折线图
  trends: {
    type: Object,
    default: () => ({})
  }
})

const chartViewBox = '0 0 100 30'

const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toLocaleString()
}

// 生成折线图点
function getSparkline(metric) {
  const trendData = props.trends[metric] || []
  if (!trendData || trendData.length < 2) return ''
  
  const max = Math.max(...trendData)
  const min = Math.min(...trendData)
  const range = max - min || 1
  
  const points = trendData.map((val, i) => {
    const x = (i / (trendData.length - 1)) * 100
    const y = 30 - ((val - min) / range) * 28 // 留2px边距
    return `${x},${y}`
  })
  
  return points.join(' ')
}
</script>

<style scoped>
.metrics-row {
  margin-bottom: 20px;
}

.metric-card {
  background: #fff;
  text-align: center;
  border-radius: 8px;
  transition: all 0.3s;
  height: 100%;
  min-height: 100px;
}

.metric-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  padding: 12px;
}

.metric-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.metric-chart {
  height: 30px;
  width: 100%;
}

.metric-chart svg {
  width: 100%;
  height: 100%;
}

@media (max-width: 1200px) {
  .metric-value {
    font-size: 14px;
  }
  .metric-label {
    font-size: 10px;
  }
}
</style>
