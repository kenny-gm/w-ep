<template>
  <div class="inventory minimal-white">
    <!-- 入库操作 -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item>
          <el-button type="primary" @click="showInboundDialog = true">手动入库</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 入库记录列表 -->
    <el-card>
      <el-table :data="records" v-loading="loading" stripe>
        <el-table-column prop="product.nm_id" label="产品ID" width="100" />
        <el-table-column label="产品名称" min-width="200">
          <template #default="{ row }">
            {{ row.product?.custom_name || row.product?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="入库数量" width="100" />
        <el-table-column prop="remaining_quantity" label="剩余" width="80" />
        <el-table-column prop="product_cost" label="产品成本" width="100">
          <template #default="{ row }">
            ₽{{ row.product_cost?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="logistics_cost" label="物流成本" width="100">
          <template #default="{ row }">
            ₽{{ row.logistics_cost?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="warehouse_type" label="仓库类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.warehouse_type === 'FBW'">FBW</el-tag>
            <el-tag v-else-if="row.warehouse_type === 'FBS'" type="warning">FBS</el-tag>
            <el-tag v-else type="info">自有</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inbound_at" label="入库时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.inbound_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="note" label="备注" min-width="150" />
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchRecords"
        @current-change="fetchRecords"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- 入库对话框 -->
    <el-dialog v-model="showInboundDialog" title="手动入库" width="500px">
      <el-form :model="inboundForm" :rules="inboundRules" ref="inboundFormRef" label-width="100px">
        <el-form-item label="产品" prop="productId">
          <el-select
            v-model="inboundForm.productId"
            filterable
            remote
            :remote-method="searchProducts"
            :loading="productLoading"
            placeholder="搜索产品"
            style="width: 100%"
          >
            <el-option
              v-for="p in productOptions"
              :key="p.id"
              :label="`${p.nm_id} - ${p.custom_name || p.name}`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="入库数量" prop="quantity">
          <el-input-number v-model="inboundForm.quantity" :min="1" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="产品成本" prop="productCost">
          <el-input-number v-model="inboundForm.productCost" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="物流成本" prop="logisticsCost">
          <el-input-number v-model="inboundForm.logisticsCost" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="仓库类型" prop="warehouseType">
          <el-radio-group v-model="inboundForm.warehouseType">
            <el-radio label="own">自有仓库</el-radio>
            <el-radio label="FBS">FBS</el-radio>
            <el-radio label="FBW">FBW</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input v-model="inboundForm.note" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showInboundDialog = false">取消</el-button>
        <el-button type="primary" @click="submitInbound">确认入库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const records = ref([])
const loading = ref(false)
const showInboundDialog = ref(false)
const productLoading = ref(false)
const productOptions = ref([])

const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

const inboundForm = reactive({
  productId: null,
  quantity: 1,
  productCost: 0,
  logisticsCost: 0,
  warehouseType: 'own',
  note: ''
})

const inboundRules = {
  productId: [{ required: true, message: '请选择产品', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  productCost: [{ required: true, message: '请输入成本', trigger: 'blur' }]
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function fetchRecords() {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.limit,
      limit: pagination.limit
    }
    const response = await axios.get('/api/inventory/records/', { params })
    records.value = response.data.items || []
    pagination.total = response.data.total || 0
  } catch (error) {
    ElMessage.error('获取入库记录失败')
  } finally {
    loading.value = false
  }
}

async function searchProducts(query) {
  if (!query) return
  
  productLoading.value = true
  try {
    const response = await axios.get('/api/products/', { params: { search: query, limit: 20 } })
    productOptions.value = response.data
  } catch (error) {
    console.error('搜索产品失败', error)
  } finally {
    productLoading.value = false
  }
}

async function submitInbound() {
  try {
    await axios.post('/api/inventory/inbound/', inboundForm)
    ElMessage.success('入库成功')
    showInboundDialog.value = false
    fetchRecords()
    
    // 重置表单
    Object.assign(inboundForm, {
      productId: null,
      quantity: 1,
      productCost: 0,
      logisticsCost: 0,
      warehouseType: 'own',
      note: ''
    })
  } catch (error) {
    ElMessage.error('入库失败')
  }
}

onMounted(() => {
  fetchRecords()
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
