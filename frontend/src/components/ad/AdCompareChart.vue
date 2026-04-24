<template>
  <el-card class="chart-card">
    <template #header>
      <div class="card-header minimal-white mw-bg">
        <span>📊 效果对比</span>
        <div class="chart-controls">
          <el-radio-group v-model="chartType" size="small">
            <el-radio-button label="line">折线图</el-radio-button>
            <el-radio-button label="bar">柱状图</el-radio-button>
            <el-radio-button label="pie">饼图</el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </template>
    <div v-if="chartType === 'pie'" ref="pieChartRef" class="chart-container"></div>
    <div v-else ref="chartRef" class="chart-container"></div>
  </el-card>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  compareMode: {
    type: Boolean,
    default: false
  }
})

const chartType = ref('line')
const chartRef = ref(null)
const pieChartRef = ref(null)
let chartInstance = null
let pieChartInstance = null

const chartColors = ['#8b5cf6', '#f59e0b', '#10b981', '#ef4444', '#3b82f6', '#ec4899']

function initLineOrBarChart() {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  // Group data by date and campaign
  const dates = [...new Set(props.data.map(d => d.date))].sort()
  const campaigns = [...new Set(props.data.map(d => d.type_name || d.type))].sort()
  
  const seriesData = campaigns.map((campaign, idx) => {
    const series = {
      name: campaign,
      type: chartType.value,
      data: dates.map(date => {
        const item = props.data.find(d => d.date === date && (d.type_name === campaign || d.type === campaign))
        return item ? (chartType.value === 'bar' ? item.spend : item.spend) : 0
      }),
      itemStyle: { color: chartColors[idx % chartColors.length] }
    }
    
    if (chartType.value === 'line') {
      series.smooth = true
      series.areaStyle = {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: chartColors[idx % chartColors.length] + '40' },
            { offset: 1, color: chartColors[idx % chartColors.length] + '05' }
          ]
        }
      }
    }
    
    return series
  })
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#ccc',
      borderWidth: 1,
      padding: 10,
      textStyle: { color: '#333' }
    },
    legend: {
      data: campaigns,
      top: 0,
      type: 'scroll'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45, fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: '₽{value}' }
    },
    series: seriesData
  }
  
  chartInstance.setOption(option)
}

function initPieChart() {
  if (!pieChartRef.value) return
  
  if (pieChartInstance) {
    pieChartInstance.dispose()
  }
  
  pieChartInstance = echarts.init(pieChartRef.value)
  
  // Aggregate spend by campaign type
  const campaignSpend = {}
  props.data.forEach(item => {
    const key = item.type_name || item.type
    campaignSpend[key] = (campaignSpend[key] || 0) + (item.spend || 0)
  })
  
  const pieData = Object.entries(campaignSpend).map(([name, value], idx) => ({
    name,
    value,
    itemStyle: { color: chartColors[idx % chartColors.length] }
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ₽{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      type: 'scroll'
    },
    series: [{
      name: '广告花费',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}: ₽{c}'
      },
      data: pieData
    }]
  }
  
  pieChartInstance.setOption(option)
}

function initChart() {
  if (chartType.value === 'pie') {
    initPieChart()
  } else {
    initLineOrBarChart()
  }
}

onMounted(() => {
  nextTick(() => {
    setTimeout(initChart, 100)
  })
})

watch([() => props.data, chartType], () => {
  nextTick(initChart)
}, { deep: true })

if (typeof window !== 'undefined') {
  window.addEventListener('resize', () => {
    chartInstance?.resize()
    pieChartInstance?.resize()
  })
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




/* 极简纯白 */
.mw-bg { background: #f8fafc; color: #0f172a; }
.mw-card { background: white !important; border: 1px solid #e2e8f0 !important; border-radius: 12px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important; }
.mw-btn-primary { background: #0f172a !important; border-color: #0f172a !important; }
.mw-btn-primary:hover { background: #334155 !important; }
.mw-table :deep(.el-table) { --el-table-bg-color: white; --el-table-tr-bg-color: white; --el-table-header-bg-color: #f8fafc; --el-table-row-hover-bg-color: #f8fafc; --el-table-border-color: #e2e8f0; --el-table-text-color: #334155; --el-table-header-text-color: #475569; }
.mw-dialog :deep(.el-dialog) { background: white !important; border-radius: 12px; }
.mw-dialog :deep(.el-dialog__title) { color: #0f172a !important; }
.mw-text { color: #0f172a; }
.mw-muted { color: #64748b !important; }
.mw-positive { color: #16a34a !important; }
.mw-negative { color: #dc2626 !important; }

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
  flex-wrap: wrap;
  gap: 8px;
}

.chart-controls {
  display: flex;
  gap: 8px;
}

.chart-container {
  width: 100%;
  height: 260px;
}
</style>
