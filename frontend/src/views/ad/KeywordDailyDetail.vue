<template>
  <div class="keyword-daily-view">
    <div class="page-header">
      <el-button @click="goBack" size="small">← 返回</el-button>
      <div class="header-info">
        <h2>{{ keyword }}</h2>
        <div class="header-meta">
          <span>日期范围: {{ dateFrom }} ~ {{ dateTo }}</span>
          <span>总花费: {{ formatNumber(totalSpend) }} ₽</span>
          <span>总点击: {{ formatNumber(totalClicks) }}</span>
          <span>总订单: {{ formatNumber(totalOrders) }}</span>
        </div>
      </div>
    </div>

    <!-- 概览卡片 -->
    <div class="overview-cards">
      <div class="overview-card">
        <div class="card-label">总花费</div>
        <div class="card-value">{{ formatNumber(totalSpend) }} ₽</div>
      </div>
      <div class="overview-card">
        <div class="card-label">总点击</div>
        <div class="card-value">{{ formatNumber(totalClicks) }}</div>
      </div>
      <div class="overview-card">
        <div class="card-label">总订单</div>
        <div class="card-value">{{ formatNumber(totalOrders) }}</div>
      </div>
      <div class="overview-card">
        <div class="card-label">平均CPC</div>
        <div class="card-value">{{ avgCpc.toFixed(2) }} ₽</div>
      </div>
      <div class="overview-card">
        <div class="card-label">平均排名</div>
        <div class="card-value">{{ avgPosition.toFixed(1) }}</div>
      </div>
    </div>

    <!-- 每日数据表格 -->
    <div class="daily-table-card">
      <h3>每日明细</h3>
      <el-table :data="dailyData" stripe style="width: 100%">
        <el-table-column prop="date" label="日期" min-width="110" />
        <el-table-column label="花费" align="right" min-width="100">
          <template #default="props">
            {{ formatNumber(props.row.spend) }} ₽
          </template>
        </el-table-column>
        <el-table-column label="点击" align="right" min-width="80">
          <template #default="props">
            {{ formatNumber(props.row.clicks) }}
          </template>
        </el-table-column>
        <el-table-column label="CPC" align="right" min-width="80">
          <template #default="props">
            {{ props.row.cpc.toFixed(2) }} ₽
          </template>
        </el-table-column>
        <el-table-column label="订单" align="right" min-width="70">
          <template #default="props">
            {{ formatNumber(props.row.orders) }}
          </template>
        </el-table-column>
        <el-table-column label="转化率" align="right" min-width="80">
          <template #default="props">
            {{ props.row.conv_rate.toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column label="平均排名" align="right" min-width="90">
          <template #default="props">
            {{ props.row.avg_position.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column label="购物车" align="right" min-width="80">
          <template #default="props">
            {{ formatNumber(props.row.atbs) }}
          </template>
        </el-table-column>
        <el-table-column label="已购数" align="right" min-width="80">
          <template #default="props">
            {{ formatNumber(props.row.shks) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const keyword = ref(route.query.keyword || '')
const dateFrom = ref(route.query.date_from || '')
const dateTo = ref(route.query.date_to || '')
const productId = ref(route.query.product_id || null)
const dailyData = ref([])
const loading = ref(true)

const totalSpend = computed(() => dailyData.value.reduce((sum, d) => sum + (d.spend || 0), 0))
const totalClicks = computed(() => dailyData.value.reduce((sum, d) => sum + (d.clicks || 0), 0))
const totalOrders = computed(() => dailyData.value.reduce((sum, d) => sum + (d.orders || 0), 0))
const avgCpc = computed(() => totalClicks.value ? totalSpend.value / totalClicks.value : 0)
const avgPosition = computed(() => {
  const withPos = dailyData.value.filter(d => d.avg_position > 0)
  if (!withPos.length) return 0
  return withPos.reduce((sum, d) => sum + d.avg_position, 0) / withPos.length
})

async function fetchData() {
  if (!productId.value || !keyword.value) return
  loading.value = true
  try {
    const response = await axios.get(`/api/products/${productId.value}/keyword-daily/`, {
      params: { keyword: keyword.value, date_from: dateFrom.value, date_to: dateTo.value }
    })
    dailyData.value = response.data.daily_data || []
  } catch (e) {
    console.error('获取关键词每日明细失败', e)
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.back()
}

function formatNumber(n) {
  if (!n && n !== 0) return '0'
  return parseFloat(n.toString().replace(/,/g, '')).toLocaleString('ru-RU')
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.keyword-daily-view {
  padding: 16px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.header-info h2 {
  margin: 0 0 8px 0;
  font-size: 18px;
  word-break: break-all;
}

.header-meta {
  display: flex;
  gap: 24px;
  font-size: 13px;
  color: #6b7280;
}

.overview-cards {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.overview-card {
  background: #f9fafb;
  border-radius: 8px;
  padding: 12px 16px;
  min-width: 120px;
  text-align: center;
}

.overview-card .card-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.overview-card .card-value {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.daily-table-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
}

.daily-table-card h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
}
</style>