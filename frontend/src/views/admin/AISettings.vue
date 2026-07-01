<template>
  <div class="ai-settings">
    <el-card>
      <template #header>
        <span>🤖 AI 大模型设置</span>
      </template>

      <div class="form-scroll-wrapper">
        <el-form :model="cfg" label-width="140px" class="settings-form" v-loading="loading">

          <el-alert type="info" :closable="false" style="margin-bottom: 16px">
            API Key 可在页面填写，由后台加密存储，不回显明文。
          </el-alert>

          <el-divider content-position="left">连接状态</el-divider>

          <el-form-item label="启用 AI">
            <el-switch v-model="cfg.enabled" :disabled="saving" />
          </el-form-item>

          <el-form-item label="API Key 状态">
            <el-tag :type="cfg.api_key_configured ? 'success' : 'danger'">
              {{ cfg.api_key_configured ? '✅ 已配置' : '❌ 未配置' }}
            </el-tag>
          </el-form-item>

          <el-form-item label="Key 来源">
            <el-tag :type="sourceTagType">{{ sourceLabel }}</el-tag>
          </el-form-item>

          <el-divider content-position="left">API Key 配置</el-divider>

          <el-form-item label="新 API Key">
            <el-input
              v-model="apiKeyInput"
              type="password"
              show-password
              :disabled="saving"
              style="width: 360px"
              placeholder="留空则不修改当前 API Key"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveSettings" :loading="saving">保存配置</el-button>
            <el-button @click="testConnection" :loading="testing" style="margin-left: 8px">测试连接</el-button>
            <el-button
              v-if="cfg.api_key_configured && cfg.api_key_source === 'database'"
              type="danger"
              plain
              @click="confirmClearKey"
              style="margin-left: 8px"
            >
              清除后台 Key
            </el-button>
          </el-form-item>

          <el-alert v-if="testResult" type="info" show-icon style="margin-top: 12px" :closable="true" @close="testResult = null">
            <template #title>
              <span v-if="testResult.success">✅ 连接成功，模型：{{ testResult.model }}</span>
              <span v-else>❌ {{ testResult.error }}</span>
            </template>
          </el-alert>

          <el-divider content-position="left">模型配置</el-divider>

          <el-form-item label="服务商">
            <el-select v-model="cfg.provider" :disabled="saving" style="width: 200px">
              <el-option value="openai" label="OpenAI"></el-option>
              <el-option value="openai_compatible" label="OpenAI 兼容（其他）"></el-option>
              <el-option value="minimax" label="MiniMax（国内版）"></el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Base URL">
            <el-input v-model="cfg.base_url" :disabled="saving" style="width: 360px" placeholder="https://api.openai.com/v1" />
            <span class="field-hint">MiniMax 国内版填 https://api.minimaxi.com/v1</span>
          </el-form-item>

          <el-form-item label="模型名称">
            <el-input v-model="cfg.model" :disabled="saving" style="width: 240px" placeholder="MiniMax-M3 / gpt-4o-mini" />
          </el-form-item>

          <el-form-item label="超时时间（秒）">
            <el-input-number v-model="cfg.timeout" :min="10" :max="300" :disabled="saving" controls-position="right" />
          </el-form-item>

          <el-form-item label="最大输出 Token">
            <el-input-number v-model="cfg.max_tokens" :min="100" :max="8000" :disabled="saving" controls-position="right" />
          </el-form-item>

        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const testResult = ref(null)
const apiKeyInput = ref('')

const cfg = reactive({
  enabled: false,
  provider: 'openai',
  base_url: 'https://api.openai.com/v1',
  model: 'gpt-4o-mini',
  api_key_configured: false,
  api_key_source: 'none',
  timeout: 60,
  max_tokens: 1200,
})

const sourceLabel = computed(() => {
  const map = {
    database: '后台数据库',
    env: '服务器环境变量',
    decrypt_error: '解密失败',
    none: '未配置',
  }
  return map[cfg.api_key_source] || '未配置'
})

const sourceTagType = computed(() => {
  const map = {
    database: 'success',
    env: 'success',
    decrypt_error: 'warning',
    none: 'info',
  }
  return map[cfg.api_key_source] || 'info'
})

async function fetchSettings() {
  loading.value = true
  try {
    const res = await axios.get('/api/ai-settings')
    cfg.enabled = res.data.enabled
    cfg.provider = res.data.provider
    cfg.base_url = res.data.base_url
    cfg.model = res.data.model
    cfg.api_key_configured = res.data.api_key_configured
    cfg.api_key_source = res.data.api_key_source || 'none'
    cfg.timeout = res.data.timeout
    cfg.max_tokens = res.data.max_tokens
  } catch (e) {
    ElMessage.error('获取 AI 配置失败')
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  try {
    const payload = {
      enabled: cfg.enabled,
      provider: cfg.provider,
      base_url: cfg.base_url,
      model: cfg.model,
      timeout: cfg.timeout,
      max_tokens: cfg.max_tokens,
    }
    if (apiKeyInput.value && apiKeyInput.value.trim() !== '') {
      payload.api_key = apiKeyInput.value.trim()
    }
    await axios.patch('/api/ai-settings', payload)
    ElMessage.success('保存成功')
    apiKeyInput.value = ''
    await fetchSettings()
  } catch (e) {
    ElMessage.error('保存失败：' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

async function confirmClearKey() {
  try {
    await ElMessageBox.confirm(
      '确定要清除后台存储的 API Key 吗？清除后如果 .env 仍有配置，将回退到环境变量。',
      '清除确认',
      { confirmButtonText: '确定清除', cancelButtonText: '取消', type: 'warning' }
    )
    await clearApiKey()
  } catch {
    // 用户取消
  }
}

async function clearApiKey() {
  try {
    const res = await axios.delete('/api/ai-settings/api-key')
    cfg.api_key_configured = res.data.api_key_configured
    cfg.api_key_source = res.data.api_key_source
    ElMessage.success('已清除后台 API Key')
  } catch (e) {
    ElMessage.error('清除失败：' + (e.response?.data?.detail || e.message))
  }
}

async function testConnection() {
  testing.value = true
  testResult.value = null
  try {
    const res = await axios.post('/api/ai-settings/test')
    testResult.value = res.data
  } catch (e) {
    testResult.value = { success: false, error: e.response?.data?.detail || e.message }
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
.ai-settings {
  padding: 20px;
}

.form-scroll-wrapper {
  overflow-x: auto;
}

.settings-form {
  min-width: 500px;
}

.field-hint {
  margin-left: 12px;
  color: #909399;
  font-size: 13px;
}
</style>