<template>
  <el-card class="chart-card">
    <template #header>
      <div class="card-header minimal-white">
        <span>📈 销售趋势 (销售额 + 广告费)</span>
      </div>
    </template>
    <div ref="chartRef" class="chart-container"></div>
  </el-card>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const chartRef = ref(null)
let chartInstance = null

function initChart() {
  if (!chartRef.value) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(chartRef.value)
  
  const dates = props.data.map(d => d.date)
  const salesData = props.data.map(d => d.sales || 0)
  const adCostData = props.data.map(d => d.ad_cost || 0)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: '#ccc',
      borderWidth: 1,
      padding: 10,
      textStyle: { color: '#333' },
      formatter: function(params) {
        if (!params || params.length === 0) return ''
        const date = params[0].axisValue
        let html = '<div style="font-weight:bold;margin-bottom:8px;">' + date + '</div>'
        params.forEach(function(param) {
          const value = param.value || 0
          html += '<div style="margin:4px 0;">' + param.marker + ' ' + param.seriesName + ': ₽' + value.toLocaleString() + '</div>'
        })
        return html
      }
    },
    legend: {
      data: ['销售额', '广告费'],
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: 45,
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '₽{value}'
      }
    },
    series: [
      {
        name: '销售额',
        type: 'line',
        smooth: true,
        data: salesData,
        itemStyle: { color: '#8b5cf6' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
              { offset: 1, color: 'rgba(139, 92, 246, 0.05)' }
            ]
          }
        }
      },
      {
        name: '广告费',
        type: 'line',
        smooth: true,
        data: adCostData,
        itemStyle: { color: '#f59e0b' }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

onMounted(() => {
  nextTick(() => {
    setTimeout(initChart, 100)
  })
})

watch(() => props.data, () => {
  nextTick(initChart)
}, { deep: true })

// 响应式
if (typeof window !== 'undefined') {
  window.addEventListener('resize', () => chartInstance?.resize())
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



.chart-card {
  height: 100%;
  min-height: 320px;
}

.card-header {
  font-weight: 600;
}

.chart-container {
  width: 100%;
  height: 220px;
}
</style>
