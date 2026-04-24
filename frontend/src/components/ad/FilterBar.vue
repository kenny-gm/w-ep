<template>
  <div class="filter-bar">
    <!-- 店铺选择 -->
    <div class="filter-item">
      <span class="filter-label">店铺</span>
      <el-select 
        v-model="localShop" 
        placeholder="选择店铺" 
        style="width: 150px"
        @change="handleShopChange"
        clearable
      >
        <el-option v-for="shop in shops" :key="shop.id" :label="shop.name" :value="shop.id" />
      </el-select>
    </div>

    <!-- 产品选择 -->
    <div class="filter-item">
      <span class="filter-label">产品</span>
      <el-select 
        v-model="localProduct" 
        filterable 
        placeholder="搜索产品" 
        style="width: 250px"
        :loading="loadingProducts"
        clearable
      >
        <el-option 
          v-for="product in filteredProducts" 
          :key="product.id" 
          :label="product.sku + ' - ' + product.name" 
          :value="product.id"
        />
      </el-select>
    </div>

    <!-- 时间快捷按钮 -->
    <div class="filter-item">
      <span class="filter-label">时间</span>
      <el-radio-group v-model="localTimeRange" size="default">
        <el-radio-button value="yesterday">昨日</el-radio-button>
        <el-radio-button value="7days">7天</el-radio-button>
        <el-radio-button value="30days">30天</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 自定义日期 -->
    <div class="filter-item">
      <span class="filter-label">自定义</span>
      <el-date-picker
        v-model="customDate"
        type="daterange"
        range-separator="至"
        start-placeholder="开始"
        end-placeholder="结束"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
        style="width: 220px"
      />
    </div>

    <!-- 查询按钮 -->
    <div class="filter-item">
      <el-button 
        type="primary" 
        @click="handleQuery" 
        :disabled="!canQuery"
        :loading="loading"
      >
        查询
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../../stores/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { token } = storeToRefs(authStore)

const props = defineProps({
  shop: { type: Number, default: null },
  product: { type: Number, default: null },
  timeRange: { type: String, default: '7days' }
})

const emit = defineEmits(['update:shop', 'update:product', 'update:time-range', 'change', 'query'])

const shops = ref([])
const products = ref([])
const loadingProducts = ref(false)
const loading = ref(false)
const customDate = ref(null)

const localShop = computed({
  get: () => props.shop,
  set: (val) => emit('update:shop', val)
})

const localProduct = computed({
  get: () => props.product,
  set: (val) => emit('update:product', val)
})

const localTimeRange = computed({
  get: () => props.timeRange,
  set: (val) => emit('update:time-range', val)
})

// 监听时间范围变化，自动更新自定义日期框
let timeRangeInit = true
watch(() => localTimeRange.value, (newRange) => {
  // 跳过首次初始化
  if (timeRangeInit) {
    timeRangeInit = false
    return
  }
  
  if (newRange && newRange !== 'custom') {
    const end = new Date()
    let start = new Date()
    
    if (newRange === 'yesterday') {
      start.setDate(end.getDate() - 1)
    } else if (newRange === '7days') {
      start.setDate(end.getDate() - 7)
    } else if (newRange === '30days') {
      start.setDate(end.getDate() - 30)
    }
    
    const fmt = (d) => d.toISOString().split('T')[0]
    customDate.value = [fmt(start), fmt(end)]
  }
})

const filteredProducts = computed(() => {
  if (!localShop.value) return products.value
  return products.value.filter(p => p.shop_id === localShop.value)
})

const canQuery = computed(() => {
  return localShop.value && localProduct.value
})

watch(() => props.shop, (newVal) => {
  if (newVal && newVal !== localShop.value) {
    localShop.value = newVal
    fetchProducts(newVal)
  }
})

const handleShopChange = async (newShopId) => {
  localProduct.value = null
  if (newShopId) {
    await fetchProducts(newShopId)
  } else {
    products.value = []
  }
}

const handleQuery = () => {
  loading.value = true
  emit('query', {
    shop: localShop.value,
    product: localProduct.value,
    timeRange: localTimeRange.value,
    customDate: customDate.value
  })
  setTimeout(() => { loading.value = false }, 500)
}

async function fetchShops() {
  try {
    const config = {
      headers: token.value ? { Authorization: `Bearer ${token.value}` } : {}
    }
    const response = await axios.get('/api/shops/', config)
    if (response.data && response.data.length > 0) {
      shops.value = response.data
      const shopId = localShop.value || shops.value[0].id
      if (!localShop.value) {
        localShop.value = shopId
      }
      await fetchProducts(shopId)
    }
  } catch (error) {
    console.error('获取店铺失败', error)
  }
}

async function fetchProducts(shopId) {
  if (!shopId) {
    products.value = []
    return
  }
  
  loadingProducts.value = true
  try {
    const config = {
      headers: token.value ? { Authorization: `Bearer ${token.value}` } : {}
    }
    const response = await axios.get('/api/shops/' + shopId + '/products/', config)
    products.value = response.data || []
    if (products.value.length > 0 && !localProduct.value) {
      localProduct.value = products.value[0].id
      emit('change')
    }
  } catch (error) {
    console.error('获取产品列表失败', error)
    products.value = []
  } finally {
    loadingProducts.value = false
  }
}

onMounted(() => {
  fetchShops()
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #f5f7fa;
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
  min-width: 36px;
}

.filter-item :deep(.el-select) {
  --el-select-input-focus-border-color: #667eea;
}

.filter-item :deep(.el-radio-button__inner) {
  border-radius: 4px;
}

.filter-item :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: #667eea;
  border-color: #667eea;
}

.filter-item :deep(.el-button--primary) {
  background: #667eea;
  border-color: #667eea;
}

@media (max-width: 1024px) {
  .filter-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .filter-item {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .filter-item :deep(.el-select),
  .filter-item :deep(.el-date-editor) {
    width: 100% !important;
  }
}
</style>
