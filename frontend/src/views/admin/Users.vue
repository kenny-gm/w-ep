<template>
  <div class="users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <el-button type="primary" @click="openCreateDialog">新增用户</el-button>
        </div>
      </template>
      
      <div class="table-scroll-wrapper">
      <el-table :data="users" v-loading="loading" stripe style="min-width: 900px;">
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="allowed_menus" label="可访问菜单" min-width="150">
          <template #default="{ row }">
            <el-tag v-if="!row.allowed_menus || row.allowed_menus.length === 0" size="small" type="info">全部菜单</el-tag>
            <el-tag v-else v-for="menu in row.allowed_menus" :key="menu" size="small" class="menu-tag">
              {{ getMenuName(menu) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="allowed_owners" label="可查看负责人" width="100" :show-overflow-tooltip="true">
          <template #default="{ row }">
            <el-tag v-if="!row.allowed_owners || row.allowed_owners.length === 0" size="small" type="info">全部</el-tag>
            <el-tag v-else v-for="owner in row.allowed_owners" :key="owner" size="small" type="success">
              {{ owner }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="editUser(row)">编辑</el-button>
            <el-button size="small" type="warning" plain @click="resetPassword(row)">重置</el-button>
            <el-button size="small" type="danger" plain @click="deleteUser(row)" :disabled="row.role === 'admin'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>
    </el-card>
    
    <!-- 创建/编辑用户对话框 -->
    <el-dialog v-model="showCreateDialog" :title="editMode ? '编辑用户' : '新增用户'" width="600px">
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="editMode" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item v-if="!editMode" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        
        <el-form-item v-if="!editMode" label="确认密码" prop="confirm_password">
          <el-input v-model="userForm.confirm_password" type="password" show-password placeholder="请再次输入密码" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" style="width: 100%" placeholder="请选择角色" @change="handleRoleChange">
            <el-option label="管理员" value="admin" />
            <el-option label="财务" value="finance" />
            <el-option label="经理" value="manager" />
            <el-option label="员工" value="staff" />
          </el-select>
        </el-form-item>
        
        <!-- 权限配置 -->
        <el-divider v-if="editMode">权限配置</el-divider>

        <!-- 客服权限级别 -->
        <el-form-item v-if="editMode" label="客服权限">
          <el-radio-group v-model="userForm.csPermissionLevel" @change="handleCsLevelChange">
            <el-radio-button value="none">无权限</el-radio-button>
            <el-radio-button value="read">只读</el-radio-button>
            <el-radio-button value="write">读写</el-radio-button>
            <el-radio-button value="custom">自定义</el-radio-button>
          </el-radio-group>
          <div class="form-tip">无权限：无法使用客服工作台 | 只读：可查看不能操作 | 读写：可执行常用客服操作 | 自定义：手动勾选具体权限</div>
        </el-form-item>

        <!-- 自定义权限勾选区 -->
        <el-form-item v-if="editMode && userForm.csPermissionLevel === 'custom'" label="">
          <div class="cs-perm-grid">
            <el-checkbox
              v-for="perm in CS_PERM_OPTIONS"
              :key="perm.value"
              :label="perm.value"
              v-model="userForm.csCustomPerms"
            >{{ perm.label }}</el-checkbox>
          </div>
        </el-form-item>

        <el-form-item v-if="editMode" label="可访问菜单">
          <el-select v-model="userForm.allowed_menus" multiple clearable placeholder="留空则可访问全部" style="width: 100%">
            <el-option
              v-for="menu in authStore.availableMenus"
              :key="menu.key"
              :label="menu.name"
              :value="menu.key"
              :disabled="menu.key === CS_MENU_KEY && userForm.csPermissionLevel === 'none'"
            />
          </el-select>
          <div class="form-tip">留空则可访问全部菜单</div>
        </el-form-item>
        
        <el-form-item v-if="editMode" label="可查看负责人">
          <el-select v-model="userForm.allowed_owners" multiple clearable placeholder="留空则可查看全部" style="width: 100%" filterable allow-create>
            <el-option v-for="owner in ownerList" :key="owner" :label="owner" :value="owner" />
          </el-select>
          <div class="form-tip">用于限制用户只能看到特定负责人的产品（以产品负责人为纬度）</div>
        </el-form-item>
        
        <el-form-item v-if="editMode" label="状态">
          <el-switch v-model="userForm.is_active" active-text="激活" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 重置密码对话框 -->
    <el-dialog v-model="showResetDialog" title="重置密码" width="400px">
      <el-form :model="resetForm" :rules="resetRules" ref="resetFormRef" label-width="100px">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="resetForm.new_password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="resetForm.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showResetDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmResetPassword" :loading="resetting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

const users = ref([])
const loading = ref(false)
const saving = ref(false)
const resetting = ref(false)
const showCreateDialog = ref(false)
const showResetDialog = ref(false)
const editMode = ref(false)
const userFormRef = ref(null)
const resetFormRef = ref(null)
const currentUser = ref(null)

// 可选的负责人列表
const ownerList = ref([])

// 获取负责人列表
async function fetchOwners() {
  try {
    const response = await axios.get('/api/admin/owners/')
    ownerList.value = response.data || []
  } catch (error) {
    console.error('获取负责人列表失败', error)
  }
}

const userForm = reactive({
  id: null,
  username: '',
  password: '',
  confirm_password: '',
  role: 'staff',
  is_active: true,
  allowed_menus: [],
  allowed_owners: [],
  // 客服权限
  csPermissionLevel: 'none',  // none / read / write / custom
  csCustomPerms: [],
})

// 客服权限选项（自定义勾选区）
const CS_PERM_OPTIONS = [
  { value: 'customer_service:read', label: '查看客服工作台' },
  { value: 'customer_service:sync', label: '同步客服数据' },
  { value: 'customer_service:translate', label: '翻译内容' },
  { value: 'customer_service:ai_draft', label: 'AI生成草稿' },
  { value: 'customer_service:note', label: '写客服备注' },
  { value: 'customer_service:status', label: '修改处理状态' },
  { value: 'customer_service:reply_feedback', label: '回复/修改评价' },
  { value: 'customer_service:answer_question', label: '回答/修改问答' },
  { value: 'customer_service:reject_question', label: '拒绝问答' },
  { value: 'customer_service:send_chat', label: '发送买家聊天' },
  { value: 'customer_service:handle_return', label: '处理退货' },
  { value: 'customer_service:admin', label: '客服管理（数据范围豁免）' },
]

// 读写权限全集（不含 admin）
const CS_READ_WRITE_PERMS = [
  'customer_service:read',
  'customer_service:sync',
  'customer_service:translate',
  'customer_service:ai_draft',
  'customer_service:note',
  'customer_service:status',
  'customer_service:reply_feedback',
  'customer_service:answer_question',
  'customer_service:reject_question',
  'customer_service:send_chat',
  'customer_service:handle_return',
]

// 从 permissions 数组推断 csPermissionLevel
function inferCsLevel(perms) {
  if (!perms || perms.length === 0) return 'none'
  const csPerms = perms.filter(p => p.startsWith('customer_service:'))
  if (csPerms.length === 0) return 'none'
  if (csPerms.length === 1 && csPerms[0] === 'customer_service:read') return 'read'
  // 检查是否等于读写全集（不含 admin，顺序无关）
  const writeablePerms = csPerms.filter(p => p !== 'customer_service:admin')
  if (writeablePerms.length === CS_READ_WRITE_PERMS.length &&
      CS_READ_WRITE_PERMS.every(p => writeablePerms.includes(p))) return 'write'
  return 'custom'
}

const CS_MENU_KEY = 'customer-service'

// csPermissionLevel 变化时更新 csCustomPerms 和 allowed_menus
function handleCsLevelChange(level) {
  if (level === 'none') {
    userForm.csCustomPerms = []
    // 从 allowed_menus 移除客服工作台
    userForm.allowed_menus = userForm.allowed_menus.filter(m => m !== CS_MENU_KEY)
  } else if (level === 'read') {
    userForm.csCustomPerms = ['customer_service:read']
    // 自动加入客服工作台菜单
    if (!userForm.allowed_menus.includes(CS_MENU_KEY)) {
      userForm.allowed_menus.push(CS_MENU_KEY)
    }
  } else if (level === 'write') {
    userForm.csCustomPerms = [...CS_READ_WRITE_PERMS]
    // 自动加入客服工作台菜单
    if (!userForm.allowed_menus.includes(CS_MENU_KEY)) {
      userForm.allowed_menus.push(CS_MENU_KEY)
    }
  }
  // custom: 保持现有 csCustomPerms 不变，allowed_menus 跟随 csCustomPerms 变化（见 watch）
}

// 监听 csCustomPerms 变化（仅 custom 模式）：自动同步 allowed_menus
watch(() => userForm.csCustomPerms.slice(), (newPerms) => {
  if (userForm.csPermissionLevel !== 'custom') return
  const hasRead = newPerms.includes('customer_service:read')
  const hasCsWrite = newPerms.some(p =>
    p.startsWith('customer_service:') && p !== 'customer_service:read'
  )
  if (hasRead) {
    // 有 read → 加入客服工作台菜单
    if (!userForm.allowed_menus.includes(CS_MENU_KEY)) {
      userForm.allowed_menus.push(CS_MENU_KEY)
    }
  } else if (hasCsWrite) {
    // 有写权限但没有 read → 补上 read（自动修复无效组合）
    userForm.csCustomPerms = ['customer_service:read', ...newPerms]
  } else {
    // 既没有 read 也没有写权限 → 移除客服工作台菜单
    userForm.allowed_menus = userForm.allowed_menus.filter(m => m !== CS_MENU_KEY)
  }
})

// 将 csPermissionLevel + csCustomPerms 转换为要提交的 permissions 数组
function buildCsPermissions() {
  const { csPermissionLevel, csCustomPerms } = userForm
  if (csPermissionLevel === 'none') return []
  if (csPermissionLevel === 'read') return ['customer_service:read']
  if (csPermissionLevel === 'write') return [...CS_READ_WRITE_PERMS]
  if (csPermissionLevel === 'custom') {
    // 自动补上 read（防止只有写权限没有 read 的无效组合）
    const hasRead = csCustomPerms.includes('customer_service:read')
    if (!hasRead && csCustomPerms.some(p => p.startsWith('customer_service:'))) {
      return ['customer_service:read', ...csCustomPerms]
    }
    return [...csCustomPerms]
  }
  return []
}

const resetForm = reactive({
  new_password: '',
  confirm_password: ''
})

const validatePass = (rule, value, callback) => {
  if (!value) callback(new Error('请输入密码'))
  else if (value.length < 6) callback(new Error('密码至少6位'))
  else callback()
}

const validatePass2 = (rule, value, callback) => {
  if (!value) callback(new Error('请再次输入密码'))
  else if (value !== userForm.password) callback(new Error('两次输入密码不一致'))
  else callback()
}

const validateResetPass2 = (rule, value, callback) => {
  if (!value) callback(new Error('请再次输入密码'))
  else if (value !== resetForm.new_password) callback(new Error('两次输入密码不一致'))
  else callback()
}

const userRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, validator: validatePass, trigger: 'blur' }],
  confirm_password: [{ required: true, validator: validatePass2, trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const resetRules = {
  new_password: [{ required: true, validator: (r, v, cb) => {
    if (!v) cb(new Error('请输入新密码'))
    else if (v.length < 6) cb(new Error('密码至少6位'))
    else cb()
  }, trigger: 'blur' }],
  confirm_password: [{ required: true, validator: validateResetPass2, trigger: 'blur' }]
}

function getRoleText(role) {
  const texts = { 'admin': '管理员', 'finance': '财务', 'manager': '经理', 'staff': '员工' }
  return texts[role] || role
}

function getRoleType(role) {
  const types = { 'admin': 'danger', 'finance': 'warning', 'manager': 'warning', 'staff': '' }
  return types[role] || ''
}

function getMenuName(key) {
  const names = { 'dashboard': '看板', 'inventory': '库存', 'orders': '订单', 'ads': '广告', 'finance': '财务' }
  return names[key] || key
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 角色变化时自动设置权限
function handleRoleChange(role) {
  if (role === 'finance') {
    userForm.allowed_menus = ['dashboard', 'orders', 'ads', 'finance']
  }
  // 切换角色时重置客服权限级别和菜单
  userForm.csPermissionLevel = 'none'
  userForm.csCustomPerms = []
  userForm.allowed_menus = []
}

async function fetchUsers() {
  loading.value = true
  try {
    const response = await axios.get('/api/admin/users/')
    users.value = response.data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  editMode.value = false
  Object.assign(userForm, {
    id: null,
    username: '',
    password: '',
    confirm_password: '',
    role: 'staff',
    is_active: true,
    allowed_menus: [],
    allowed_owners: [],
    csPermissionLevel: 'none',
    csCustomPerms: [],
  })
  showCreateDialog.value = true
}

function editUser(user) {
  editMode.value = true
  Object.assign(userForm, {
    id: user.id,
    username: user.username,
    role: user.role,
    is_active: user.is_active,
    allowed_menus: user.allowed_menus || [],
    allowed_owners: user.allowed_owners || [],
    // 客服权限：从 permissions 推断级别
    csPermissionLevel: inferCsLevel(user.permissions),
    csCustomPerms: (user.permissions || []).filter(p => p.startsWith('customer_service:')),
  })
  showCreateDialog.value = true
}

async function saveUser() {
  const valid = await userFormRef.value?.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  try {
    const data = {
      role: userForm.role,
      is_active: userForm.is_active,
      allowed_menus: userForm.allowed_menus,
      allowed_owners: userForm.allowed_owners,
      permissions: buildCsPermissions(),
    }
    
    if (editMode.value) {
      await axios.put(`/api/admin/users/${userForm.id}/`, data)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/admin/users/', userForm)
      ElMessage.success('创建成功')
    }
    
    showCreateDialog.value = false
    fetchUsers()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

function resetPassword(user) {
  currentUser.value = user
  resetForm.new_password = ''
  resetForm.confirm_password = ''
  showResetDialog.value = true
}

async function confirmResetPassword() {
  const valid = await resetFormRef.value?.validate().catch(() => false)
  if (!valid) return
  
  resetting.value = true
  try {
    await axios.post(`/api/admin/users/${currentUser.value.id}/reset-password/?new_password=${resetForm.new_password}`)
    ElMessage.success('密码已重置')
    showResetDialog.value = false
  } catch (error) {
    ElMessage.error('重置失败')
  } finally {
    resetting.value = false
  }
}

async function deleteUser(user) {
  await ElMessageBox.confirm(`确定删除用户 ${user.username}？`, '确认删除', { type: 'warning' })
  
  try {
    await axios.delete(`/api/admin/users/${user.id}/`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  authStore.fetchMenus()
  fetchUsers()
  fetchOwners()
})
</script>

<style scoped>
.users-page {
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

.menu-tag {
  margin-right: 5px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.cs-perm-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px 16px;
  padding: 4px 0;
}
</style>
