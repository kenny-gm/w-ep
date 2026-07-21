<template>
  <div class="metric-thresholds">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📊 指标预警阈值设置</span>
          <div>
            <el-button type="primary" size="small" @click="addThreshold">
              <el-icon><Plus /></el-icon> 添加指标
            </el-button>
          </div>
        </div>
      </template>

      <div class="table-scroll-wrapper">
      <el-table :data="thresholds" v-loading="loading" stripe style="min-width: 1000px;">
        <el-table-column label="指标名称" width="150" fixed="left">
          <template #default="{ row }">
            <el-select 
              v-model="row.metric_name" 
              size="small" 
              placeholder="请选择指标"
              :disabled="!row.isNew && row.metric_name"
              style="width: 100%"
              filterable
              @change="onMetricSelect(row)"
            >
              <el-option
                v-for="metric in presetMetrics"
                :key="metric.value"
                :label="metric.label"
                :value="metric.value"
              />
              <el-option
                v-if="!presetMetrics.find(m => m.value === row.metric_name) && row.metric_name"
                :key="row.metric_name"
                :label="'自定义: ' + row.metric_name"
                :value="row.metric_name"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column prop="display_name" label="显示名称" width="120">
          <template #default="{ row }">
            <el-input v-model="row.display_name" size="small" placeholder="显示名称" />
          </template>
        </el-table-column>
        
        <el-table-column label="预警阈值" width="120">
          <template #default="{ row }">
            <el-input-number 
              v-model="row.warning_threshold" 
              :min="0" 
              :precision="2"
              size="small"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="危险阈值" width="120">
          <template #default="{ row }">
            <el-input-number 
              v-model="row.danger_threshold" 
              :min="0" 
              :precision="2"
              size="small"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="比较方式" width="120">
          <template #default="{ row }">
            <el-select v-model="row.comparison" size="small">
              <el-option label="大于等于" value="greater_than" />
              <el-option label="小于等于" value="less_than" />
            </el-select>
          </template>
        </el-table-column>
        
        <el-table-column label="颜色预览" width="200">
          <template #default="{ row }">
            <div class="color-preview">
              <div class="color-item">
                <span class="color-dot" :style="{ background: row.good_color }"></span>
                <span>正常</span>
              </div>
              <div class="color-item">
                <span class="color-dot" :style="{ background: row.warning_color }"></span>
                <span>预警</span>
              </div>
              <div class="color-item">
                <span class="color-dot" :style="{ background: row.danger_color }"></span>
                <span>危险</span>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="颜色设置" width="140">
          <template #default="{ row }">
            <div class="color-settings">
              <el-color-picker v-model="row.good_color" size="small" />
              <el-color-picker v-model="row.warning_color" size="small" />
              <el-color-picker v-model="row.danger_color" size="small" />
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleSave(row)">
              保存
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>

      <!-- 说明 -->
      <div class="help-section">
        <el-alert
          title="阈值规则说明"
          type="info"
          :closable="false"
        >
          <ul class="help-list">
            <li><strong>大于等于(greater_than)</strong>：指标值 ≥ 预警阈值显示预警色，≥ 危险阈值显示危险色</li>
            <li><strong>小于等于(less_than)</strong>：指标值 ≤ 预警阈值显示预警色，≤ 危险阈值显示危险色</li>
            <li>示例：转化率设置 greater_than 2.0/1.0，表示低于2%预警，低于1%危险</li>
            <li>示例：广告占比设置 less_than 15.0/25.0，表示高于15%预警，高于25%危险</li>
          </ul>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import axios from 'axios'

const thresholds = ref([])
const loading = ref(false)

// 预设指标列表（基于系统标准字段命名）
const presetMetrics = ref([
  // 核心业务指标
  { value: 'cart_rate', label: '加购率 (cart_rate)' },
  { value: 'conversion_rate', label: '转化率 (conversion_rate)' },
  { value: 'ad_ratio', label: '广告占比 (ad_ratio)' },
  
  // 标准计数字段（根据MEMORY.md规范）
  { value: 'visitors', label: '访客数 (visitors)' },
  { value: 'cart_count', label: '加购数 (cart_count)' },
  { value: 'order_count', label: '订单数 (order_count)' },
  { value: 'order_sum', label: '销售额 (order_sum)' },
  
  // 广告相关字段
  { value: 'impressions', label: '广告曝光 (impressions)' },
  { value: 'cost', label: '广告花费 (cost)' },
  { value: 'ad_visitors', label: '广告访客 (ad_visitors)' },
  
  // 财务指标
  { value: 'roi', label: '投资回报率 (roi)' },
  { value: 'acos', label: '广告销售成本比 (acos)' },
  { value: 'profit_margin', label: '利润率 (profit_margin)' },
  
  // 其他常用指标
  { value: 'ctr', label: '点击率 (ctr)' },
  { value: 'cpc', label: '每次点击成本 (cpc)' },
  { value: 'bounce_rate', label: '跳出率 (bounce_rate)' },
  { value: 'average_order_value', label: '平均订单价值 (average_order_value)' },
  
  // 自定义比率指标
  { value: 'refund_rate', label: '退款率 (refund_rate)' },
  { value: 'stockout_rate', label: '缺货率 (stockout_rate)' },
  { value: 'fulfillment_rate', label: '履约率 (fulfillment_rate)' }
])

// 获取配置列表
async function fetchThresholds() {
  loading.value = true
  try {
    const response = await axios.get('/api/metric-thresholds/')
    // 调试：检查返回的数据类型
    console.log('Fetched thresholds:', response.data)
    if (response.data && response.data.length > 0) {
      console.log('First threshold is_active:', response.data[0].is_active, 'type:', typeof response.data[0].is_active)
    }
    
    // 确保is_active是布尔值（处理可能从API返回的整数）
    const processedData = (response.data || []).map(item => {
      return {
        ...item,
        is_active: item.is_active === true || item.is_active === 1 || item.is_active === 'true' || item.is_active === '1'
      }
    })
    
    thresholds.value = processedData
  } catch (error) {
    console.error('获取配置失败', error)
    ElMessage.error('获取配置失败')
  } finally {
    loading.value = false
  }
}

// 添加新指标
function addThreshold() {
  thresholds.value.push({
    metric_name: '',
    display_name: '',
    warning_threshold: 0,
    danger_threshold: 0,
    comparison: 'greater_than',
    good_color: '#10b981',
    warning_color: '#f59e0b',
    danger_color: '#ef4444',
    is_active: true,
    isNew: true
  })
}

// 根据选择的指标自动填充显示名称
function onMetricSelect(row) {
  if (row.metric_name && !row.display_name) {
    const metric = presetMetrics.value.find(m => m.value === row.metric_name)
    if (metric) {
      // 从label中提取中文名称
      const label = metric.label
      const chineseName = label.split(' (')[0]
      row.display_name = chineseName
    }
  }
}

// 保存配置
async function handleSave(row) {
  if (!row.metric_name) {
    ElMessage.warning('请输入指标名称')
    return
  }
  
  try {
    if (row.isNew) {
      await axios.post('/api/metric-thresholds/', {
        metric_name: row.metric_name,
        warning_threshold: row.warning_threshold,
        danger_threshold: row.danger_threshold,
        comparison: row.comparison,
        display_name: row.display_name,
        good_color: row.good_color,
        warning_color: row.warning_color,
        danger_color: row.danger_color,
        is_active: row.is_active
      })
    } else {
      await axios.put(`/api/metric-thresholds/${row.metric_name}/`, {
        warning_threshold: row.warning_threshold,
        danger_threshold: row.danger_threshold,
        comparison: row.comparison,
        display_name: row.display_name,
        good_color: row.good_color,
        warning_color: row.warning_color,
        danger_color: row.danger_color,
        is_active: row.is_active
      })
    }
    ElMessage.success('保存成功')
    fetchThresholds()
  } catch (error) {
    console.error('保存失败', error)
    ElMessage.error('保存失败')
  }
}

// 删除配置
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除该指标阈值吗？', '提示', {
      type: 'warning'
    })
    
    await axios.delete(`/api/metric-thresholds/${row.metric_name}/`)
    ElMessage.success('删除成功')
    fetchThresholds()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchThresholds()
})
</script>

<style scoped>
.metric-thresholds {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.color-preview {
  display: flex;
  gap: 12px;
}

.color-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 1px solid #dcdfe6;
}

.color-settings {
  display: flex;
  gap: 8px;
}

.help-section {
  margin-top: 20px;
}

.help-list {
  margin: 8px 0 0 0;
  padding-left: 20px;
  line-height: 1.8;
}

.help-list li {
  margin-bottom: 4px;
}

.table-scroll-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.table-scroll-wrapper::-webkit-scrollbar {
  height: 4px;
}

.table-scroll-wrapper::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 2px;
}

@media (max-width: 768px) {
  .metric-thresholds {
    padding: 12px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .color-preview {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .color-settings {
    flex-wrap: wrap;
  }
  
  .el-table {
    font-size: 12px;
  }
  
  .el-table :deep(.el-table__cell) {
    padding: 8px 4px;
  }
  
  .table-scroll-wrapper {
    margin: 0 -12px;
    padding: 0 12px;
  }
}
</style>
