<template>
  <div class="ai-settings">
    <el-card>
      <template #header>
        <span>🤖 AI 大模型设置</span>
      </template>

      <div class="form-scroll-wrapper">
        <el-form :model="cfg" label-width="140px" class="settings-form" v-loading="loading">

          <el-alert type="info" :closable="false" style="margin-bottom: 16px">
            API Key 仅通过服务器 <code>.env</code> 文件配置，页面不显示也不保存 Key。
          </el-alert>

          <el-divider content-position="left">连接状态</el-divider>

          <el-form-item label="启用 AI">
            <el-switch v-model="cfg.enabled" :disabled="saving" />
          </el-form-item>

          <el-form-item label="API Key 状态">
            <el-tag :type="cfg.api_key_configured ? 'success' : 'danger'">
              {{ cfg.api_key_configured ? '✅ 已配置' : '❌ 未配置' }}
            </el-tag>
            <span class="field-hint">在服务器 .env 中配置 AI_API_KEY（MiniMax / OpenAI 均可）</span>
          </el-form-item>

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

          <el-divider />

          <el-form-item>
            <el-button type="primary" @click="saveSettings" :loading="saving">保存配置</el-button>
            <el-button @click="testConnection" :loading="testing" style="margin-left: 8px">测试连接</el-button>
          </el-form-item>

          <el-alert v-if="testResult" type="info" show-icon style="margin-top: 12px" :closable="true" @close="testResult = null">
            <template #title>
              <span v-if="testResult.success">✅ 连接成功，模型：{{ testResult.model }}</span>
              <span v-else>❌ {{ testResult.error }}</span>
            </template>
          </el-alert>

        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const testResult = ref(null)

const cfg = reactive({
  enabled: false,
  provider: 'openai',
  base_url: 'https://api.openai.com/v1',
  model: 'gpt-4.1-mini',
  api_key_configured: false,
  timeout: 60,
  max_tokens: 1200,
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
    await axios.patch('/api/ai-settings', {
      enabled: cfg.enabled,
      provider: cfg.provider,
      base_url: cfg.base_url,
      model: cfg.model,
      timeout: cfg.timeout,
      max_tokens: cfg.max_tokens,
    })
    ElMessage.success('保存成功')
    await fetchSettings()
  } catch (e) {
    ElMessage.error('保存失败：' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
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
