<template>
  <div class="alerts-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔔 预警中心</span>
          <el-badge :value="unreadCount" :hidden="unreadCount === 0">
            <el-button size="small">未读</el-button>
          </el-badge>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="未读预警" name="unread">
          <el-empty v-if="unreadAlerts.length === 0" description="暂无未读预警" />
          <div v-else>
            <el-card v-for="alert in unreadAlerts" :key="alert.id" class="alert-card" :class="alert.severity">
              <template #header>
                <div class="alert-header">
                  <el-tag :type="getSeverityType(alert.severity)">{{ getSeverityText(alert.severity) }}</el-tag>
                  <span class="alert-title">{{ alert.title }}</span>
                  <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
                </div>
              </template>
              <div class="alert-content">
                <p>{{ alert.content }}</p>
              </div>
              <div class="alert-actions">
                <el-button type="success" size="small" @click="showProcessDialog(alert)">处理预警</el-button>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="全部预警" name="all">
          <el-empty v-if="allAlerts.length === 0" description="暂无预警" />
          <div v-else class="table-scroll-wrapper">
            <el-table :data="allAlerts" stripe style="min-width: 900px;">
              <el-table-column prop="title" label="预警标题" min-width="200" />
              <el-table-column prop="alert_type" label="类型" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ getTypeText(row.alert_type) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="severity" label="级别" width="80">
                <template #default="{ row }">
                  <el-tag :type="getSeverityType(row.severity)" size="small">{{ getSeverityText(row.severity) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_read" label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.is_read ? 'info' : 'danger'" size="small">{{ row.is_read ? '已读' : '未读' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="时间" width="160">
                <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button link type="success" size="small" @click="showProcessDialog(row)" v-if="!row.is_resolved">处理</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div class="pagination">
            <el-pagination
              v-model:current-page="pagination.page"
              :page-size="pagination.pageSize"
              :total="pagination.total"
              layout="total, prev, pager, next"
              @current-change="fetchAlerts"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <el-dialog v-model="processDialogVisible" title="处理预警" width="500px">
      <el-form :model="processForm" label-width="100px">
        <el-form-item label="处理方式">
          <el-select v-model="processForm.action_type" placeholder="请选择处理方式">
            <el-option label="调整广告" value="adjust_ad" />
            <el-option label="优化价格" value="update_price" />
            <el-option label="优化页面" value="optimize_page" />
            <el-option label="忽略" value="ignore" />
          </el-select>
        </el-form-item>
        <el-form-item label="跟踪天数">
          <el-input-number v-model="processForm.tracking_days" :min="1" :max="30" />
        </el-form-item>
        <el-form-item label="处理说明">
          <el-input v-model="processForm.content" type="textarea" :rows="3" placeholder="请输入处理说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="processDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProcess">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const activeTab = ref('unread')
const unreadAlerts = ref([])
const allAlerts = ref([])
const unreadCount = ref(0)
const processDialogVisible = ref(false)
const currentAlert = ref(null)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const processForm = reactive({
  action_type: 'adjust_ad',
  tracking_days: 7,
  content: ''
})

function formatTime(time) {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

function getSeverityType(severity) {
  const map = { danger: 'danger', warning: 'warning', info: 'info' }
  return map[severity] || 'info'
}

function getSeverityText(severity) {
  const map = { danger: '危险', warning: '警告', info: '提示' }
  return map[severity] || '提示'
}

function getTypeText(type) {
  const map = { acos: 'ACOS', profit: '利润', conversion: '转化率', cart_rate: '加购率', ad_ratio: '广告占比' }
  return map[type] || type
}

async function fetchUnreadAlerts() {
  try {
    const response = await axios.get('/api/alerts/unread/')
    unreadAlerts.value = response.data
    unreadCount.value = response.data.length
  } catch (error) {
    console.error('获取未读预警失败', error)
  }
}

async function fetchAlerts() {
  try {
    const response = await axios.get('/api/alerts/', {
      params: { skip: (pagination.page - 1) * pagination.pageSize, limit: pagination.pageSize }
    })
    allAlerts.value = response.data.items || []
    pagination.total = response.data.total || 0
  } catch (error) {
    console.error('获取预警失败', error)
  }
}

function showProcessDialog(alert) {
  currentAlert.value = alert
  processForm.content = ''
  processForm.action_type = 'adjust_ad'
  processForm.tracking_days = 7
  processDialogVisible.value = true
}

async function submitProcess() {
  if (!processForm.content) {
    ElMessage.warning('请输入处理说明')
    return
  }
  try {
    await axios.post('/api/alerts/' + currentAlert.value.id + '/process/', processForm)
    ElMessage.success('预警已处理')
    processDialogVisible.value = false
    fetchUnreadAlerts()
    fetchAlerts()
  } catch (error) {
    ElMessage.error('处理失败')
  }
}

onMounted(() => {
  fetchUnreadAlerts()
  fetchAlerts()
})
</script>

<style scoped>
.alerts-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.alert-card { margin-bottom: 16px; }
.alert-card.danger { border-left: 4px solid #f56c6c; }
.alert-card.warning { border-left: 4px solid #e6a23c; }
.alert-header { display: flex; align-items: center; gap: 12px; }
.alert-title { font-weight: 600; flex: 1; }
.alert-time { color: #909399; font-size: 12px; }
.alert-content { margin-bottom: 12px; }
.alert-actions { display: flex; gap: 8px; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
.table-scroll-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.table-scroll-wrapper::-webkit-scrollbar { height: 4px; }
.table-scroll-wrapper::-webkit-scrollbar-thumb { background: #dcdfe6; border-radius: 2px; }

@media (max-width: 768px) {
  .alerts-container { padding: 12px; }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .alert-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .alert-title {
    font-size: 14px;
  }
  
  .alert-content {
    font-size: 13px;
  }
  
  .alert-actions {
    flex-wrap: wrap;
  }
  
  .pagination {
    justify-content: center;
  }
  
  .el-dialog {
    width: 95% !important;
    margin: 10px auto;
  }
}
</style>
