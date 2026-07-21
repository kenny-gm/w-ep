<template>
  <div class="menu-settings-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>侧边栏菜单管理</span>
          <el-button type="primary" @click="openCreateDialog">新增菜单</el-button>
        </div>
      </template>
      
      <div class="table-scroll-wrapper">
        <el-table :data="menus" v-loading="loading" row-key="id" :tree-props="{ children: 'children' }" style="min-width: 900px;">
        <el-table-column prop="name" label="菜单名称" min-width="150" fixed="left">
          <template #default="{ row }">
            <span>{{ row.icon }} {{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="key" label="标识" width="120" />
        <el-table-column prop="path" label="路由" min-width="150" />
        <el-table-column prop="required_role" label="权限" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.required_role" size="small" :type="row.required_role === 'admin' ? 'danger' : ''">
              {{ row.required_role }}
            </el-tag>
            <span v-else class="text-gray">所有用户</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_visible" label="显示" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.is_visible" @change="toggleVisible(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editMenu(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteMenu(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>
      
      <div class="tips">
        <el-alert type="info" :closable="false">
          <template #title>
            <span>💡 提示：拖拽排序功能开发中，目前可通过编辑修改 sort_order 数值来调整顺序</span>
          </template>
        </el-alert>
      </div>
    </el-card>
    
    <!-- 创建/编辑菜单对话框 -->
    <el-dialog v-model="showDialog" :title="editMode ? '编辑菜单' : '新增菜单'" width="500px">
      <el-form :model="menuForm" :rules="menuRules" ref="menuFormRef" label-width="100px">
        <el-form-item label="标识key" prop="key">
          <el-input v-model="menuForm.key" :disabled="editMode" placeholder="如: products, dashboard" />
        </el-form-item>
        
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="menuForm.name" placeholder="如: 产品管理" />
        </el-form-item>
        
        <el-form-item label="图标">
          <el-input v-model="menuForm.icon" placeholder="如: Goods (Element Plus图标名)">
            <template #append>
              <span>{{ getIconPreview(menuForm.icon) }}</span>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="路由路径" prop="path">
          <el-input v-model="menuForm.path" placeholder="如: /products, /dashboard" />
        </el-form-item>
        
        <el-form-item label="父级菜单">
          <el-select v-model="menuForm.parent_key" clearable placeholder="无（顶级菜单）">
            <el-option v-for="m in parentMenus" :key="m.key" :label="m.name" :value="m.key" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="所需权限">
          <el-select v-model="menuForm.required_role" clearable placeholder="所有用户可访问">
            <el-option label="仅管理员" value="admin" />
            <el-option label="管理员和经理" value="manager" />
            <el-option label="所有用户" :value="null" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="排序">
          <el-input-number v-model="menuForm.sort_order" :min="0" :max="999" />
        </el-form-item>
        
        <el-form-item label="是否显示">
          <el-switch v-model="menuForm.is_visible" active-text="显示" inactive-text="隐藏" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveMenu" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const menus = ref([])
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const editMode = ref(false)
const menuFormRef = ref(null)

const menuForm = reactive({
  id: null,
  key: '',
  name: '',
  icon: '',
  path: '',
  parent_key: null,
  sort_order: 0,
  is_visible: true,
  required_role: null
})

const menuRules = {
  key: [{ required: true, message: '请输入标识key', trigger: 'blur' }],
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
  path: [{ required: true, message: '请输入路由路径', trigger: 'blur' }]
}

// 父级菜单列表（只显示顶级菜单）
const parentMenus = computed(() => menus.value.filter(m => !m.parent_key))

function getIconPreview(icon) {
  return icon ? '📌' : '—'
}

// 构建树形结构
function buildTree(items) {
  const map = {}
  const roots = []
  
  items.forEach(item => {
    item.children = []
    map[item.id] = item
  })
  
  items.forEach(item => {
    if (item.parent_key && map[item.parent_key]) {
      map[item.parent_key].children.push(item)
    } else {
      roots.push(item)
    }
  })
  
  return roots.sort((a, b) => a.sort_order - b.sort_order)
}

async function fetchMenus() {
  loading.value = true
  try {
    const response = await axios.get('/api/admin/menus/')
    menus.value = buildTree(response.data || [])
  } catch (error) {
    console.error('获取菜单失败', error)
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  editMode.value = false
  Object.assign(menuForm, {
    id: null,
    key: '',
    name: '',
    icon: '',
    path: '',
    parent_key: null,
    sort_order: menus.value.length,
    is_visible: true,
    required_role: null
  })
  showDialog.value = true
}

function editMenu(menu) {
  editMode.value = true
  Object.assign(menuForm, {
    id: menu.id,
    key: menu.key,
    name: menu.name,
    icon: menu.icon,
    path: menu.path,
    parent_key: menu.parent_key,
    sort_order: menu.sort_order,
    is_visible: menu.is_visible,
    required_role: menu.required_role
  })
  showDialog.value = true
}

async function saveMenu() {
  const valid = await menuFormRef.value?.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  try {
    const data = { ...menuForm }
    if (!data.parent_key) data.parent_key = null
    if (!data.required_role) data.required_role = null
    
    if (editMode.value) {
      await axios.put(`/api/admin/menus/${menuForm.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/admin/menus/', data)
      ElMessage.success('创建成功')
    }
    
    showDialog.value = false
    fetchMenus()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function toggleVisible(menu) {
  try {
    await axios.put(`/api/admin/menus/${menu.id}`, { is_visible: menu.is_visible })
    ElMessage.success('已更新')
  } catch (error) {
    ElMessage.error('更新失败')
    menu.is_visible = !menu.is_visible
  }
}

async function deleteMenu(menu) {
  await ElMessageBox.confirm(`确定删除菜单 "${menu.name}"？`, '确认删除', {
    type: 'warning'
  })
  
  try {
    await axios.delete(`/api/admin/menus/${menu.id}`)
    ElMessage.success('删除成功')
    fetchMenus()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchMenus()
})
</script>

<style scoped>
.menu-settings-page {
  padding: 0;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tips {
  margin-top: 20px;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}
</style>
