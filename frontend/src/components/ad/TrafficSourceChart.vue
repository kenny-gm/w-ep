<template>
  <el-card class="chart-card" shadow="hover">
    <template #header>
      <div class="card-header minimal-white">
        <span>📊 流量来源分析</span>
        <div class="header-stats" v-if="data.total_visitors">
          <span class="stat">总访客: {{ formatNumber(data.total_visitors) }}</span>
        </div>
      </div>
    </template>
    <div ref="chartRef" class="chart-container"></div>
    <div class="source-legend">
      <div class="legend-item">
        <span class="dot natural"></span>
        <span>自然流量 {{ data.natural_ratio || 0 }}%</span>
        <span class="visitor-count">({{ formatNumber(data.natural_visitors) }} 访客)</span>
      </div>
      <div class="legend-item">
        <span class="dot ad"></span>
        <span>广告流量 {{ data.ad_ratio || 0 }}%</span>
        <span class="visitor-count">({{ formatNumber(data.ad_visitors) }} 访客)</span>
      </div>
      <div class="legend-item" v-if="data.other_ratio > 0">
        <span class="dot other"></span>
        <span>其他流量 {{ data.other_ratio || 0 }}%</span>
        <span class="visitor-count">({{ formatNumber(data.other_visitors) }} 访客)</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { formatNumber } from '../../utils/currency'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      natural_ratio: 0,
      ad_ratio: 0,
      other_ratio: 0,
      natural_visitors: 0,
      ad_visitors: 0,
      other_visitors: 0,
      total_visitors: 0
    })
  }
})

const chartRef = ref(null)
let chartInstance = null

function initChart() {
  if (!chartRef.value) return
  
  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {d}% ({c} 访客)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['自然流量', '广告流量', '其他流量'],
      show: false
    },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      label: {
        show: true,
        formatter: '{b}: {d}%'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      data: [
        { 
          value: props.data.natural_visitors || 0, 
          name: '自然流量', 
          itemStyle: { color: '#10b981' } 
        },
        { 
          value: props.data.ad_visitors || 0, 
          name: '广告流量', 
          itemStyle: { color: '#8b5cf6' } 
        },
        { 
          value: props.data.other_visitors || 0, 
          name: '其他流量', 
          itemStyle: { color: '#f59e0b' } 
        }
      ]
    }]
  }
  
  chartInstance.setOption(option)
}

onMounted(() => {
  nextTick(() => {
    setTimeout(initChart, 100)
  })
  window.addEventListener('resize', () => chartInstance?.resize())
})

watch(() => props.data, () => {
  nextTick(() => initChart())
}, { deep: true })
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



.chart-card {
  height: 100%;
  min-height: 320px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 14px;
}

.header-stats {
  font-size: 12px;
  color: #909399;
}

.stat {
  margin-left: 10px;
}

.chart-container {
  width: 100%;
  height: 220px;
}

.source-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.visitor-count {
  font-size: 11px;
  color: #909399;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.natural { background: #10b981; }
.dot.ad { background: #8b5cf6; }
.dot.other { background: #f59e0b; }
</style>
