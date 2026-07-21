<template>
  <div class="admin-settings">
    <el-card>
      <template #header>系统设置</template>
      
      <div class="form-scroll-wrapper">
      <el-form :model="settings" label-width="120px" class="settings-form">
        <el-divider content-position="left">汇率设置</el-divider>
        
        <el-form-item label="人民币转卢布汇率">
          <el-input-number v-model="settings.cny_to_rub" :min="0" :precision="4" :step="0.1" controls-position="right" />
          <span class="rate-hint">1 CNY = {{ settings.cny_to_rub }} RUB</span>
        </el-form-item>
        
        <el-divider />
        
        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
      </div>
    </el-card>
    
    <el-card style="margin-top: 20px">
      <template #header>系统信息</template>
      
      <el-descriptions :column="1" border class="info-descriptions">
        <el-descriptions-item label="系统名称">{{ systemName }}</el-descriptions-item>
        <el-descriptions-item label="版本">{{ systemInfo.version }}</el-descriptions-item>
        <el-descriptions-item label="运行环境">{{ systemInfo.app_env }}</el-descriptions-item>
        <el-descriptions-item label="后端框架">{{ systemInfo.backend_framework }}</el-descriptions-item>
        <el-descriptions-item label="前端框架">{{ systemInfo.frontend_framework }}</el-descriptions-item>
        <el-descriptions-item label="数据库">{{ databaseDisplay }}</el-descriptions-item>
        <el-descriptions-item label="部署方式">{{ systemInfo.deployment }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const systemName = ref('WB ERP')

const systemInfo = reactive({
  version: '1.0.0',
  app_env: '-',
  backend_framework: 'FastAPI',
  frontend_framework: 'Vue 3 + Element Plus',
  database: '-',
  database_host: '',
  database_name: '',
  deployment: 'Docker'
})

const settings = reactive({
  cny_to_rub: 12.5
})

const databaseDisplay = computed(() => {
  const parts = [systemInfo.database]
  if (systemInfo.database_host && systemInfo.database_host !== 'local') {
    parts.push(systemInfo.database_host)
  }
  if (systemInfo.database_name) {
    parts.push(systemInfo.database_name)
  }
  return parts.filter(Boolean).join(' / ')
})

async function fetchSettings() {
  try {
    const response = await axios.get('/api/admin/settings/')
    
    if (response.data.cny_to_rub) {
      settings.cny_to_rub = parseFloat(response.data.cny_to_rub)
    }
  } catch (error) {
    console.error('获取设置失败', error)
  }
}

async function fetchUISettings() {
  try {
    const response = await axios.get('/api/admin/ui-settings/')
    if (response.data.system_name) {
      systemName.value = response.data.system_name
    }
  } catch (error) {
    // 忽略
  }
}

async function fetchSystemInfo() {
  try {
    const response = await axios.get('/api/admin/system-info/')
    Object.assign(systemInfo, response.data)
    if (response.data.system_name) {
      systemName.value = response.data.system_name
    }
  } catch (error) {
    console.error('获取系统信息失败', error)
  }
}

async function saveSettings() {
  try {
    await axios.put('/api/admin/settings/cny_to_rub/', { value: settings.cny_to_rub.toString() })
    
    ElMessage.success('保存成功')
    // 保存后重新加载最新数据
    await fetchSettings()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  fetchSettings()
  fetchUISettings()
  fetchSystemInfo()
})
</script>

<style scoped>
.admin-settings {
  padding: 20px;
}

.form-scroll-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.settings-form {
  min-width: 500px;
}

.rate-hint {
  margin-left: 10px;
  color: #909399;
  font-size: 13px;
  white-space: nowrap;
}

.info-descriptions {
  min-width: 300px;
}

@media (max-width: 768px) {
  .admin-settings {
    padding: 12px;
  }
  
  .settings-form {
    min-width: 0;
  }
  
  .el-form-item {
    margin-bottom: 16px;
  }
  
  .el-divider {
    margin: 16px 0;
  }
  
  .el-input-number {
    width: 100%;
  }
}
</style>
