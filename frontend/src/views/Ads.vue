<template>
  <div class="ads minimal-white">
    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始"
            end-placeholder="结束"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="fetchAds"
          />
        </el-form-item>
        
        <el-form-item label="广告类型">
          <el-select v-model="filters.adType" placeholder="全部" style="width: 150px" @change="fetchAds">
            <el-option label="全部" :value="null" />
            <el-option label="搜索广告" value="search" />
            <el-option label="推荐广告" value="recommend" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="店铺">
          <el-select v-model="filters.shopId" placeholder="全部" style="width: 150px" @change="fetchAds">
            <el-option label="全部" :value="null" />
            <el-option v-for="shop in shops" :key="shop.id" :label="shop.name" :value="shop.id" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 广告数据表 -->
    <el-card>
      <el-table :data="ads" v-loading="loading" stripe>
        <el-table-column prop="product.nm_id" label="产品ID" width="100" />
        <el-table-column label="产品名称" min-width="150">
          <template #default="{ row }">
            {{ row.product?.custom_name || row.product?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="ad_type" label="广告类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.ad_type === 'search'" type="primary">搜索</el-tag>
            <el-tag v-else type="success">推荐</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="impressions" label="展示量" width="100" />
        <el-table-column prop="clicks" label="点击量" width="100" />
        <el-table-column prop="ctr" label="点击率" width="80">
          <template #default="{ row }">
            {{ (row.ctr * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="花费" width="100">
          <template #default="{ row }">
            ₽{{ row.cost?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="sales" label="销售额" width="100">
          <template #default="{ row }">
            ₽{{ row.sales?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="acos" label="ACOS" width="80">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.acos > 0.3 }">
              {{ (row.acos * 100).toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="cpc" label="CPC" width="80">
          <template #default="{ row }">
            ₽{{ row.cpc?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="cpm" label="CPM" width="80">
          <template #default="{ row }">
            ₽{{ row.cpm?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="roas" label="ROAS" width="80">
          <template #default="{ row }">
            {{ row.roas?.toFixed(2) }}
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchAds"
        @current-change="fetchAds"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- 优化建议 -->
    <el-card class="suggestions-card">
      <template #header>优化建议</template>
      <div v-if="suggestions.length === 0" class="empty-suggestion">暂无建议</div>
      <div v-for="(s, i) in suggestions" :key="i" class="suggestion-item">
        <el-tag :type="s.type" size="small">{{ s.level }}</el-tag>
        <span class="suggestion-text">{{ s.text }}</span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const ads = ref([])
const shops = ref([])
const loading = ref(false)
const dateRange = ref([])
const suggestions = ref([])

const filters = reactive({
  shopId: null,
  adType: null
})

const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

async function fetchAds() {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.limit,
      limit: pagination.limit
    }
    
    if (filters.shopId) params.shop_id = filters.shopId
    if (filters.adType) params.ad_type = filters.adType
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const response = await axios.get('/api/ads/', { params })
    ads.value = response.data.items || []
    pagination.total = response.data.total || 0
    
    generateSuggestions()
  } catch (error) {
    ElMessage.error('获取广告数据失败')
  } finally {
    loading.value = false
  }
}

async function fetchShops() {
  try {
    const response = await axios.get('/api/shops/')
    shops.value = response.data
  } catch (error) {
    console.error('获取店铺失败', error)
  }
}

function generateSuggestions() {
  suggestions.value = []
  
  ads.value.forEach(ad => {
    const productName = ad.product?.custom_name || ad.product?.name || ad.product?.nm_id
    
    // ACOS 过高
    if (ad.acos > 0.3) {
      suggestions.value.push({
        level: '警告',
        type: 'danger',
        text: `【${productName}】ACOS 过高 (${(ad.acos * 100).toFixed(1)}%)，建议降低出价或优化关键词`
      })
    }
    
    // 点击率低
    if (ad.ctr < 0.01 && ad.impressions > 100) {
      suggestions.value.push({
        level: '建议',
        type: 'warning',
        text: `【${productName}】点击率较低 (${(ad.ctr * 100).toFixed(2)}%)，建议优化主图或标题`
      })
    }
    
    // ROAS 低
    if (ad.roas < 2 && ad.cost > 100) {
      suggestions.value.push({
        level: '建议',
        type: 'info',
        text: `【${productName}】ROAS 较低 (${ad.roas.toFixed(2)})，建议检查落地页或价格`
      })
    }
  })
  
  if (suggestions.value.length > 10) {
    suggestions.value = suggestions.value.slice(0, 10)
  }
}

onMounted(() => {
  // 默认最近7天
  const today = new Date()
  const weekAgo = new Date(today)
  weekAgo.setDate(weekAgo.getDate() - 7)
  dateRange.value = [
    weekAgo.toISOString().split('T')[0],
    today.toISOString().split('T')[0]
  ]
  
  fetchAds()
  fetchShops()
})
</script>

<style scoped>
/* 极简纯白全局样式 */
.minimal-white {
  padding: 16px;
  min-height: 100vh;
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



.filter-card {
  margin-bottom: 20px;
}

.suggestions-card {
  margin-top: 20px;
}

.empty-suggestion {
  color: #909399;
  text-align: center;
  padding: 20px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-text {
  font-size: 14px;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}
</style>
