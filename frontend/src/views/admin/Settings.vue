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
        
        <el-divider content-position="left">同步设置</el-divider>
        
        <el-form-item label="自动同步">
          <el-switch v-model="settings.sync_enabled" />
        </el-form-item>
        
        <el-form-item label="同步时间">
          <el-input-number v-model="settings.sync_hour" :min="0" :max="23" controls-position="right" />
          <span class="rate-hint">每天凌晨 {{ settings.sync_hour }}:00</span>
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
        <el-descriptions-item label="版本">1.0.0</el-descriptions-item>
        <el-descriptions-item label="后端框架">FastAPI</el-descriptions-item>
        <el-descriptions-item label="前端框架">Vue 3 + Element Plus</el-descriptions-item>
        <el-descriptions-item label="数据库">SQLite</el-descriptions-item>
        <el-descriptions-item label="部署方式">Docker</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const systemName = ref('WB ERP')

const settings = reactive({
  cny_to_rub: 12.5,
  sync_enabled: true,
  sync_hour: 3
})

async function fetchSettings() {
  try {
    const response = await axios.get('/api/admin/settings/')
    
    if (response.data.cny_to_rub) {
      settings.cny_to_rub = parseFloat(response.data.cny_to_rub)
    }
    if (response.data.sync_enabled !== undefined) {
      settings.sync_enabled = response.data.sync_enabled === 'true'
    }
    if (response.data.sync_hour) {
      settings.sync_hour = parseInt(response.data.sync_hour)
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

async function saveSettings() {
  try {
    await axios.put('/api/admin/settings/cny_to_rub/', { value: settings.cny_to_rub.toString() })
    await axios.put('/api/admin/settings/sync_enabled/', { value: settings.sync_enabled.toString() })
    await axios.put('/api/admin/settings/sync_hour/', { value: settings.sync_hour.toString() })
    
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
