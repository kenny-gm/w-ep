<template>
  <div class="products minimal-white">
    <!-- 筛选和操作 -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="店铺">
          <el-select v-model="filters.shopId" placeholder="全部店铺" style="width: 150px" @change="fetchProducts">
            <el-option label="全部店铺" :value="null" />
            <el-option v-for="shop in shops" :key="shop.id" :label="shop.name" :value="shop.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="负责人">
          <el-select v-model="filters.owner" placeholder="全部" style="width: 150px" @change="fetchProducts">
            <el-option label="全部" :value="null" />
            <el-option v-for="owner in ownerList" :key="owner" :label="owner" :value="owner" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="产品名称/SKU" clearable @keyup.enter="fetchProducts" style="width: 200px">
            <template #append>
              <el-button :icon="Search" @click="fetchProducts" />
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item v-if="authStore.isAdmin">
          <el-button type="primary" @click="showSyncDialog = true">同步产品</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 产品列表 -->
    <el-card>
      <el-table :data="products" v-loading="loading" stripe>
        <el-table-column prop="nm_id" label="产品ID" width="100" />
        <el-table-column prop="sku" label="SKU" width="150" />
        <el-table-column label="店铺" width="120">
          <template #default="{ row }">
            {{ getShopName(row.shop_id) }}
          </template>
        </el-table-column>
        <el-table-column label="产品名称" min-width="200">
          <template #default="{ row }">
            <span>{{ row.custom_name || row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="owner" label="负责人" width="100" />
        <el-table-column label="重量(kg)" width="100">
          <template #default="{ row }">
            {{ row.weight || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="尺寸(cm)" width="120">
          <template #default="{ row }">
            <span v-if="row.length">{{ row.length }}×{{ row.width }}×{{ row.height }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editProduct(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        :total="pagination.total"
        :page-sizes="[20, 50, 100, 200]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchProducts"
        @current-change="fetchProducts"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- 编辑产品对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑产品" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="产品ID">
          <el-input v-model="editForm.nm_id" disabled />
        </el-form-item>
        <el-form-item label="产品名称">
          <el-input v-model="editForm.custom_name" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="editForm.owner" />
        </el-form-item>
        <el-form-item label="重量(kg)">
          <el-input-number v-model="editForm.weight" :min="0" :precision="3" style="width: 100%" />
        </el-form-item>
        <el-form-item label="长度(cm)">
          <el-input-number v-model="editForm.length" :min="0" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="宽度(cm)">
          <el-input-number v-model="editForm.width" :min="0" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="高度(cm)">
          <el-input-number v-model="editForm.height" :min="0" :precision="1" style="width: 100%" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 同步对话框 -->
    <el-dialog v-model="showSyncDialog" title="同步产品" width="400px">
      <el-form label-width="80px">
        <el-form-item label="选择店铺">
          <el-select v-model="syncShopId" placeholder="请选择店铺" style="width: 100%">
            <el-option v-for="shop in shops" :key="shop.id" :label="shop.name" :value="shop.id" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showSyncDialog = false">取消</el-button>
        <el-button type="primary" :loading="syncing" @click="syncProducts">开始同步</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const products = ref([])
const shops = ref([])

// 根据店铺ID获取店铺名称
function getShopName(shopId) {
  const shop = shops.value.find(s => s.id === shopId)
  return shop ? shop.name : '-'
}

const ownerList = ref([])
const loading = ref(false)
const editDialogVisible = ref(false)
const showSyncDialog = ref(false)
const syncing = ref(false)
const syncShopId = ref(null)

const filters = reactive({
  shopId: null,
  owner: null,
  search: ''
})

const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

const editForm = reactive({
  id: null,
  nm_id: '',
  custom_name: '',
  owner: '',
  weight: null,
  length: null,
  width: null,
  height: null
})

async function fetchProducts() {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.limit,
      limit: pagination.limit
    }
    
    if (filters.shopId) params.shop_id = filters.shopId
    if (filters.owner) params.owner = filters.owner
    if (filters.search) params.search = filters.search
    
    const response = await axios.get('/api/products/', { params })
    products.value = response.data
    // 设置总数用于分页
    const totalHeader = response.headers['x-total']
    if (totalHeader) {
      pagination.total = parseInt(totalHeader)
    } else if (response.data.length > 0 && response.data[0]._total !== undefined) {
      pagination.total = response.data[0]._total
    }
  } catch (error) {
    ElMessage.error('获取产品列表失败')
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

async function fetchOwners() {
  try {
    const response = await axios.get('/api/products/owners/')
    ownerList.value = response.data
  } catch (error) {
    console.error('获取负责人失败', error)
  }
}

function editProduct(product) {
  Object.assign(editForm, {
    id: product.id,
    nm_id: product.nm_id,
    custom_name: product.custom_name,
    owner: product.owner,
    weight: product.weight,
    length: product.length,
    width: product.width,
    height: product.height
  })
  editDialogVisible.value = true
}

async function saveProduct() {
  try {
    await axios.put(`/api/products/${editForm.id}/`, {
      custom_name: editForm.custom_name,
      owner: editForm.owner,
      weight: editForm.weight,
      length: editForm.length,
      width: editForm.width,
      height: editForm.height
    })
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    fetchProducts()
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  }
}

async function syncProducts() {
  if (!syncShopId.value) {
    ElMessage.warning('请选择店铺')
    return
  }
  
  syncing.value = true
  try {
    const response = await axios.post(`/api/products/sync/${syncShopId.value}`)
    ElMessage.success(response.data.message)
    showSyncDialog.value = false
    fetchProducts()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '同步失败')
  } finally {
    syncing.value = false
  }
}

onMounted(() => {
  fetchProducts()
  fetchShops()
  fetchOwners()
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
</style>
