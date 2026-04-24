<template>
  <el-card class="chart-card" shadow="hover">
    <template #header>
      <div class="card-header minimal-white mw-bg">
        <span>📊 广告类型访客趋势</span>
        <el-radio-group v-model="chartType" size="small">
          <el-radio-button label="line">折线图</el-radio-button>
          <el-radio-button label="bar">柱状图</el-radio-button>
        </el-radio-group>
      </div>
    </template>
    <div ref="chartRef" class="chart-container"></div>
    <div class="source-legend">
      <div class="legend-item" v-for="item in legendData" :key="item.name">
        <span class="dot" :style="{ background: item.color }"></span>
        <span>{{ item.name }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed } from "vue"
import * as echarts from "echarts"

const props = defineProps({
  data: {
    type: Object,
    default: () => ({
      total_visitors: 0,
      ad_types: []
    })
  }
})

const chartType = ref("line")
const chartRef = ref(null)
let chartInstance = null

const legendData = computed(() => {
  if (!props.data.ad_types || props.data.ad_types.length === 0) {
    return []
  }
  return props.data.ad_types.map(item => ({
    name: item.name,
    color: item.color
  }))
})

function initChart() {
  if (!chartRef.value) return
  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value)
  
  const chartData = props.data.ad_types || []
  const dates = ["03-20", "03-19", "03-18", "03-17", "03-16", "03-15", "03-14"]
  
  const series = chartData.map((item) => ({
    name: item.name,
    type: chartType.value,
    data: item.visitors_data || [820, 932, 901, 934, 890, 930, 920],
    itemStyle: { color: item.color },
    smooth: chartType.value === "line",
    areaStyle: chartType.value === "line" ? {
      color: {
        type: "linear", x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: item.color + "40" },
          { offset: 1, color: item.color + "05" }
        ]
      }
    } : undefined
  }))
  
  const option = {
    tooltip: { trigger: "axis" },
    grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
    xAxis: { type: "category", data: dates, axisLabel: { rotate: 45, fontSize: 11 } },
    yAxis: { type: "value", name: "访客数" },
    series
  }
  
  chartInstance.setOption(option)
}

onMounted(() => {
  nextTick(() => { setTimeout(initChart, 100) })
  window.addEventListener("resize", () => chartInstance?.resize())
})

watch(() => props.data, () => { nextTick(() => initChart()) }, { deep: true })
watch(chartType, () => { nextTick(() => initChart()) })
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



.chart-card { height: 100%; min-height: 320px; }
.card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 14px; }
.chart-container { width: 100%; height: 220px; }
.source-legend { display: flex; justify-content: center; gap: 16px; margin-top: 12px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #606266; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
</style>
