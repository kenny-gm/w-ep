<template>
  <el-card class="ad-table-card" shadow="hover">
    <template #header>
      <div class="table-header">
        <span class="table-title">广告活动数据</span>
        <el-radio-group v-model="localActiveType" size="small" @change="handleTabChange">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="cpm_search">CPM搜索</el-radio-button>
          <el-radio-button label="cpm_recommend">CPM推荐</el-radio-button>
          <el-radio-button label="cpc_search">CPC搜索</el-radio-button>
        </el-radio-group>
      </div>
    </template>

    <div class="table-wrapper">
      <el-table :data="filteredData" stripe border size="small">
        <el-table-column prop="date" label="日期" width="100" fixed="left" />

        <el-table-column prop="type_name" label="类型" width="90">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" size="small">{{ row.type_name }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="impressions" label="展示量" width="80" />
        <el-table-column prop="clicks" label="点击" width="70" />
        <el-table-column prop="ctr" label="点击率" width="70">
          <template #default="{ row }">
            <span>{{ row.ctr != null ? (row.ctr * 100).toFixed(2) : '-' }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="orders" label="订单" width="60" />
        <el-table-column prop="spend" label="花费" width="80">
          <template #default="{ row }">{{ formatRuble(row.spend || row.cost, false) }}</template>
        </el-table-column>
        <el-table-column prop="sales" label="销售额" width="90">
          <template #default="{ row }">{{ formatRuble(row.sales, false) }}</template>
        </el-table-column>
        <el-table-column prop="cpc" label="CPC" width="70">
          <template #default="{ row }">{{ row.cpc != null ? '₽' + row.cpc.toFixed(2) : '-' }}</template>
        </el-table-column>
        <el-table-column prop="cpm" label="CPM" width="70">
          <template #default="{ row }">{{ row.cpm != null ? '₽' + row.cpm.toFixed(2) : '-' }}</template>
        </el-table-column>
        <el-table-column prop="acos" label="ACOS" width="70">
          <template #default="{ row }">
            <span v-if="row.acos != null">{{ (row.acos * 100).toFixed(1) }}%</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="roas" label="ROAS" width="70">
          <template #default="{ row }">
            <span v-if="row.roas != null">{{ row.roas.toFixed(1) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { formatRuble } from '../../utils/currency'

const props = defineProps({
  data: { type: Array, required: true },
  activeType: { type: String, default: 'all' }
})

const emit = defineEmits(['tab-change'])

const localActiveType = computed({
  get: () => props.activeType,
  set: (val) => emit('tab-change', val)
})

const filteredData = computed(() => {
  if (localActiveType.value === 'all') return props.data || []
  return (props.data || []).filter(item => item.type === localActiveType.value)
})

const handleTabChange = (val) => {
  emit('tab-change', val)
}

function getTypeTag(type) {
  const map = { cpm_search: 'primary', cpm_recommend: 'success', cpc_search: 'warning' }
  return map[type] || 'info'
}
</script>

<style scoped>
.ad-table-card { margin-bottom: 16px; }
.table-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.table-title { font-size: 14px; font-weight: 600; color: #0f172a; }
.table-wrapper { overflow-x: auto; }
:deep(.el-table) { font-size: 12px; }
:deep(.el-table th) { background-color: #f5f7fa; color: #606266; font-weight: 600; }
:deep(.el-table td) { padding: 6px 4px; }
</style>