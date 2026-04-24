<template>
  <div class="product-analysis minimal-white">
    <div class="analysis-layout">
      <!-- 左侧店铺列表 -->
      <div class="left-sidebar">
        <div class="sidebar-header">
          <span>连接</span>
        </div>
        <div class="shop-list">
          <div 
            v-for="shop in shops" 
            :key="shop.id"
            class="shop-item"
            :class="{ active: filters.shopId === shop.id }"
            @click="selectShop(shop.id)"
          >
            <el-icon><Shop /></el-icon>
            <span class="shop-name">{{ shop.name }}</span>
            <el-tag v-if="shop.hasNewData" size="small" type="success">新</el-tag>
          </div>
        </div>
        
        <el-divider />
        
        <!-- 快速筛选 -->
        <div class="quick-filters">
          <div class="filter-section-title">快速筛选</div>
          <div 
            v-for="filter in quickFilters" 
            :key="filter.key"
            class="quick-filter-item"
            :class="{ active: activeQuickFilter === filter.key }"
            @click="toggleQuickFilter(filter)"
          >
            <span>{{ filter.label }}</span>
            <el-badge :value="filter.count" :type="filter.type" />
          </div>
        </div>
        
        <el-divider />
        
        <!-- 标签筛选 -->
        <div class="tags-filter-section">
          <div class="filter-section-title">标签</div>
          <el-input v-model="tagSearch" placeholder="搜索标签" size="small" style="margin-bottom: 8px" />
          <div class="tags-list">
            <el-checkbox 
              v-for="tag in filteredAvailableTags" 
              :key="tag"
              v-model="selectedTags"
              :label="tag"
              @change="handleTagFilterChange"
            >{{ tag }}</el-checkbox>
          </div>
          <el-button link type="primary" size="small" @click="showCreateTag = true" style="margin-top: 8px">+ 创建标签</el-button>
        </div>
      </div>
      
      <!-- 主内容区 -->
      <div class="main-content">
        <!-- 顶部工具栏 -->
        <div class="top-toolbar">
          <div class="toolbar-left">
            <!-- 日期范围 -->
            <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 240px"
            />
            
            <!-- 数据更新时间 -->
            <span class="update-info">
              <el-icon><Clock /></el-icon>
              更新: {{ lastUpdateTime }}
              <el-button link type="primary" size="small" @click="refreshData" :loading="loading">
                {{ loading ? '更新中...' : '1小时前' }}
              </el-button>
            </span>
          </div>
          
          <div class="toolbar-right">
            <!-- 角色选择 -->
            <el-dropdown @command="handleRoleCommand" trigger="click">
              <el-button type="default">
                <el-icon><User /></el-icon>
                {{ currentRole.name }}
                <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="role in roles" :key="role.id" :command="'role:' + role.id">
                    {{ role.name }}
                    <el-icon v-if="role.id === currentRole.id"><Check /></el-icon>
                  </el-dropdown-item>
                  <el-dropdown-item command="createRole" divided>
                    <el-icon><Plus /></el-icon>
                    创建新角色
                  </el-dropdown-item>
                  <el-dropdown-item command="manageRole" v-if="currentRole.id !== 'default'">
                    <el-icon><Setting /></el-icon>
                    编辑角色
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <!-- 视图管理 -->
            <el-dropdown @command="handleViewCommand">
              <el-button type="default">
                <el-icon><Document /></el-icon>
                视图
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="saveView">保存当前视图</el-dropdown-item>
                  <el-dropdown-item command="resetView">重置为默认</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <!-- 列设置 -->
            <el-popover placement="bottom-end" :width="300" trigger="click">
              <template #reference>
                <el-button type="default">
                  <el-icon><Grid /></el-icon>
                  列
                </el-button>
              </template>
              <div class="column-settings">
                <div class="column-settings-header">
                  <span>选择表格列</span>
                  <el-button link type="primary" size="small" @click="resetColumns">重置</el-button>
                </div>
                <div class="column-list">
                  <el-checkbox 
                    v-for="col in allColumns" 
                    :key="col.prop" 
                    v-model="col.visible"
                    :label="col.label"
                    @change="saveColumnSettings"
                  />
                </div>
              </div>
            </el-popover>
            
            <!-- 导出 -->
            <el-dropdown @command="handleExportCommand">
              <el-button type="default">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="csv">导出 CSV</el-dropdown-item>
                  <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
                  <el-dropdown-item command="selected">导出选中项</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
        
        <!-- 指标卡片区 -->
        <div class="metrics-panel">
          <div class="metrics-header">
            <span class="metrics-title">主要商品指标</span>
            <div class="metrics-actions">
              <el-button link type="primary" size="small" @click="showMetricSettings = true">
                <el-icon><Setting /></el-icon>
                设置
              </el-button>
            </div>
          </div>
          <div class="metrics-grid">
            <div 
              v-for="(metric, idx) in activeMetrics" 
              :key="metric.key"
              class="metric-card"
              :class="{ active: metric.active, [metric.status || 'normal']: true }"
              :style="{ order: metric.order }"
              draggable="true"
              @dragstart="onMetricDragStart($event, idx)"
              @dragover.prevent
              @drop="onMetricDrop(idx)"
              @click="toggleMetricFilter(metric)"
            >
              <div class="metric-header">
                <span class="metric-label">{{ metric.label }}</span>
                <el-tooltip :content="metric.description" placement="top">
                  <el-icon class="metric-help"><QuestionFilled /></el-icon>
                </el-tooltip>
              </div>
              <div class="metric-value">{{ metric.value || '-' }}</div>
              <div class="metric-sub" v-if="metric.subValue">{{ metric.subValue }}</div>
              <div class="metric-filter-info" v-if="metric.active">
                <span v-if="metric.filterType === 'lt'">&lt; {{ metric.filterValue }}</span>
                <span v-else-if="metric.filterType === 'gt'">&gt; {{ metric.filterValue }}</span>
                <el-icon class="filter-clear" @click.stop="clearMetricFilter(metric)"><Close /></el-icon>
              </div>
              <!-- 拖拽手柄 -->
              <div class="metric-drag-handle" @click.stop>
                <el-icon><Rank /></el-icon>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 表格工具栏 -->
        <div class="table-toolbar">
          <div class="toolbar-left">
            <!-- 搜索 -->
            <el-input
              v-model="filters.search"
              placeholder="搜索产品名称、SKU、NM_ID"
              clearable
              style="width: 260px"
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <!-- 批量操作 -->
            <el-dropdown @command="handleBatchCommand" :disabled="selectedProducts.length === 0">
              <el-button type="default">
                批量操作 ({{ selectedProducts.length }})
                <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="batchTag">编辑标签</el-dropdown-item>
                  <el-dropdown-item command="batchCost">编辑成本</el-dropdown-item>
                  <el-dropdown-item command="batchExport">导出选中</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          
          <div class="toolbar-right">
            <!-- 仓库分布 -->
            <el-button link type="primary" @click="showWarehouseDetail = true">
              <el-icon><OfficeBuilding /></el-icon>
              仓库分布
            </el-button>
          </div>
        </div>
        
        <!-- 数据表格 -->
        <div class="table-container" @mousedown="startCellSelection" @mousemove="extendCellSelection" @mouseup="endCellSelection">
          <el-table
            ref="productTableRef"
            :data="displayProducts"
            v-loading="loading"
            stripe
            @selection-change="handleSelectionChange"
            @sort-change="handleSortChange"
            :default-sort="{ prop: 'sales', order: 'descending' }"
            @row-click="handleRowClick"
            @row-dblclick="handleRowDblClick"
            class="product-table"
            :row-class-name="getRowClassName"
            :span-method="cellSpanMethod"
          >
            <el-table-column type="selection" width="40" :selectable="checkSelectable" />
            
            <el-table-column
              v-for="col in visibleColumns"
              :key="col.prop"
              :prop="col.prop"
              :label="col.label"
              :width="col.width"
              :min-width="col.minWidth"
              :sortable="col.sortable ? 'custom' : false"
              :fixed="col.fixed"
              :align="col.align || 'left'"
              :class-name="getColumnClassName(col.prop)"
              @click="handleColumnHeaderClick(col)"
            >
              <template #header>
                <span class="column-header">
                  {{ col.label }}
                  <el-tooltip v-if="col.filterHint" :content="col.filterHint" placement="top">
                    <el-icon class="filter-hint"><Filter /></el-icon>
                  </el-tooltip>
                </span>
              </template>
              
              <template #default="{ row, $index }">
                <!-- 标签列 -->
                <template v-if="col.prop === 'tags'">
                  <div class="tags-cell">
                    <el-tag 
                      v-for="tag in (row.tags || [])" 
                      :key="tag" 
                      size="small" 
                      type="info"
                      :class="'tag-' + tag"
                    >
                      {{ tag }}
                    </el-tag>
                    <el-button 
                      link 
                      type="primary" 
                      size="small"
                      @click.stop="openTagDialog([row])"
                    >
                      +标签
                    </el-button>
                  </div>
                </template>
                
                <!-- 仓库分布列 -->
                <template v-else-if="col.prop === 'warehouse'">
                  <el-popover placement="bottom" :width="280" trigger="click">
                    <template #reference>
                      <span class="warehouse-link">
                        {{ row.warehouse }}
                        <el-icon><ArrowRight /></el-icon>
                      </span>
                    </template>
                    <div class="warehouse-detail-popover">
                      <div class="warehouse-detail-title">{{ row.name }}</div>
                      <div v-for="(qty, wh, idx) in row.warehouseDetail" :key="idx" class="warehouse-row">
                        <span class="wh-name">{{ wh }}</span>
                        <span class="wh-qty">{{ qty }}件</span>
                      </div>
                      <div class="warehouse-footer">
                        <el-button link type="primary" size="small" @click="showWarehouseDetail = true">查看全部</el-button>
                      </div>
                    </div>
                  </el-popover>
                </template>
                
                <!-- 价格相关列 -->
                <template v-else-if="col.prop === 'price'">
                  <span class="price-cell">
                    {{ formatPrice(row.price) }} ₽
                  </span>
                </template>
                
                <template v-else-if="col.prop === 'finalPrice'">
                  <span class="price-cell final-price">
                    {{ formatPrice(row.finalPrice) }} ₽
                  </span>
                </template>
                
                <template v-else-if="col.prop === 'discount'">
                  <span class="discount-badge" v-if="row.discount > 0">
                    -{{ row.discount }}%
                  </span>
                  <span v-else>-</span>
                </template>
                
                <!-- 数量列 -->
                <template v-else-if="col.prop === 'stock'">
                  <span :class="{ 'low-stock': row.stock < 10, 'out-of-stock': row.stock === 0 }">
                    {{ row.stock }}
                    <el-icon v-if="row.stock === 0" color="#ef4444"><WarningFilled /></el-icon>
                    <el-icon v-else-if="row.stock < 10" color="#f59e0b"><Warning /></el-icon>
                  </span>
                </template>
                
                <template v-else-if="col.prop === 'sales'">
                  <span class="sales-cell">
                    {{ formatNumber(row.sales) }} ₽
                  </span>
                </template>
                
                <!-- 比率列 -->
                <template v-else-if="col.prop === 'profitRate'">
                  <span :class="getRateClass(row.profitRate)">
                    {{ row.profitRate }}%
                  </span>
                </template>
                
                <template v-else-if="col.prop === 'conversionRate'">
                  <span>{{ row.conversionRate }}%</span>
                </template>
                
                <!-- 评分列 -->
                <template v-else-if="col.prop === 'rating'">
                  <span class="rating-cell" v-if="row.rating">
                    <el-icon color="#f59e0b"><Star /></el-icon>
                    {{ row.rating }}
                    <span v-if="row.ratingCount" class="rating-count">({{ row.ratingCount }})</span>
                  </span>
                  <span v-else>-</span>
                </template>
                
                <!-- 操作列 -->
                <template v-else-if="col.prop === 'actions'">
                  <el-dropdown trigger="click" @command="handleProductAction($event, row)" @click.stop>
                    <el-button link type="primary" size="small">
                      <el-icon><More /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="detail">
                          <el-icon><View /></el-icon>
                          查看详情
                        </el-dropdown-item>
                        <el-dropdown-item command="edit">
                          <el-icon><Edit /></el-icon>
                          编辑产品
                        </el-dropdown-item>
                        <el-dropdown-item command="cost">
                          <el-icon><Money /></el-icon>
                          编辑成本
                        </el-dropdown-item>
                        <el-dropdown-item command="price">
                          <el-icon><PriceTag /></el-icon>
                          编辑价格
                        </el-dropdown-item>
                        <el-dropdown-item command="supply">
                          <el-icon><Box /></el-icon>
                          供应链计算
                        </el-dropdown-item>
                        <el-dropdown-item command="ad">
                          <el-icon><TrendCharts /></el-icon>
                          查看广告
                        </el-dropdown-item>
                        <el-dropdown-item command="history">
                          <el-icon><Clock /></el-icon>
                          历史走势
                        </el-dropdown-item>
                        <el-dropdown-item command="source" divided>
                          <el-icon><Link /></el-icon>
                          WB原始页面
                        </el-dropdown-item>
                        <el-dropdown-item command="copy">
                          <el-icon><CopyDocument /></el-icon>
                          复制链接
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </template>
                
                <!-- 其他列 -->
                <template v-else>
                  {{ row[col.prop] || '-' }}
                </template>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 底部统计栏 -->
        <div class="table-footer">
          <div class="footer-left">
            <span>已选择 <strong>{{ selectedProducts.length }}</strong> 项</span>
            <el-divider direction="vertical" />
            <span>共 <strong>{{ filteredProducts.length }}</strong> 件商品</span>
            <el-divider direction="vertical" />
            <span class="selection-summary" v-if="selectedProducts.length > 0">
              选中合计：
              <span class="stat-item">销售额 <strong>{{ formatNumber(selectedSalesTotal) }} ₽</strong></span>
              <span class="stat-item">订单 <strong>{{ selectedOrdersTotal }}</strong></span>
              <span class="stat-item">利润 <strong>{{ formatNumber(selectedProfitTotal) }} ₽</strong></span>
            </span>
          </div>
          <div class="footer-right">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.pageSize"
              :page-sizes="[20, 50, 100, 200, 500]"
              :total="filteredProducts.length"
              layout="sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- 标签编辑弹窗 -->
    <el-dialog v-model="tagDialogVisible" title="编辑产品标签" width="500px">
      <div class="tag-edit-info">
        已选择 {{ editingProducts.length }} 个产品
      </div>
      <el-form>
        <el-form-item label="选择标签">
          <el-checkbox-group v-model="selectedTagList">
            <el-checkbox 
              v-for="tag in availableTags" 
              :key="tag" 
              :label="tag"
            >
              {{ tag }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="添加新标签">
          <el-input v-model="newTagInput" placeholder="输入新标签名称">
            <template #append>
              <el-button @click="addNewTag" :disabled="!newTagInput">添加</el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tagDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProductTags">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 创建标签弹窗 -->
    <el-dialog v-model="showCreateTag" title="创建标签" width="400px">
      <el-form>
        <el-form-item label="标签名称">
          <el-input v-model="newTagName" placeholder="输入标签名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateTag = false">取消</el-button>
        <el-button type="primary" @click="confirmCreateTag">创建</el-button>
      </template>
    </el-dialog>
    
    <!-- 指标设置弹窗 -->
    <el-dialog v-model="showMetricSettings" title="指标设置" width="600px">
      <div class="metric-settings-info">
        选择要在顶部卡片区域显示的指标。点击卡片可筛选对应产品，拖拽可调整顺序。
      </div>
      <div class="metric-settings-list">
        <div v-for="metric in allMetrics" :key="metric.key" class="metric-setting-item">
          <el-checkbox v-model="metric.enabled" @change="saveMetricSettings">
            {{ metric.label }}
          </el-checkbox>
          <span class="metric-setting-desc">{{ metric.description }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="showMetricSettings = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 指标筛选弹窗 -->
    <el-dialog v-model="showMetricFilterDialog" title="设置筛选条件" width="400px">
      <el-form v-if="editingMetric">
        <el-form-item :label="editingMetric.label">
          <el-radio-group v-model="editingMetric.filterType" class="filter-type-group">
            <el-radio label="lt">小于</el-radio>
            <el-radio label="gt">大于</el-radio>
            <el-radio label="eq">等于</el-radio>
          </el-radio-group>
          <el-input-number 
            v-model="editingMetric.filterValue" 
            :min="0" 
            :precision="2" 
            style="width: 100%; margin-top: 12px" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMetricFilterDialog = false">取消</el-button>
        <el-button type="primary" @click="applyMetricFilter">应用筛选</el-button>
      </template>
    </el-dialog>
    
    <!-- 角色管理弹窗 -->
    <el-dialog v-model="showRoleDialog" :title="roleDialogTitle" width="450px">
      <el-form v-if="editingRole">
        <el-form-item label="角色名称">
          <el-input v-model="editingRole.name" placeholder="输入角色名称" />
        </el-form-item>
        <el-form-item label="角色描述">
          <el-input v-model="editingRole.description" type="textarea" :rows="2" placeholder="可选描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRoleDialog = false">取消</el-button>
        <el-button type="danger" @click="deleteRole" v-if="editingRole && editingRole.id !== 'default'">
          删除
        </el-button>
        <el-button type="primary" @click="saveRole">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 仓库详情弹窗 -->
    <el-dialog v-model="showWarehouseDetail" title="仓库库存分布" width="600px">
      <el-table :data="warehouseDetailList" stripe>
        <el-table-column prop="warehouse" label="仓库" />
        <el-table-column prop="quantity" label="库存数量" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.quantity) }} 件
          </template>
        </el-table-column>
        <el-table-column prop="percent" label="占比" align="right">
          <template #default="{ row }">
            {{ row.percent }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button link type="primary" @click="filterByWarehouse(row)">筛选</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
    
    <!-- 产品详情抽屉 -->
    <el-drawer v-model="showProductDetail" :title="currentProduct?.name || '产品详情'" size="600px">
      <div class="product-detail" v-if="currentProduct">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="NM_ID">{{ currentProduct.nmId }}</el-descriptions-item>
          <el-descriptions-item label="SKU">{{ currentProduct.sku }}</el-descriptions-item>
          <el-descriptions-item label="价格">{{ formatPrice(currentProduct.price) }} ₽</el-descriptions-item>
          <el-descriptions-item label="最终价">{{ formatPrice(currentProduct.finalPrice) }} ₽</el-descriptions-item>
          <el-descriptions-item label="库存">{{ currentProduct.stock }}</el-descriptions-item>
          <el-descriptions-item label="仓库">{{ currentProduct.warehouse }}</el-descriptions-item>
          <el-descriptions-item label="销售额" :span="2">{{ formatNumber(currentProduct.sales) }} ₽</el-descriptions-item>
          <el-descriptions-item label="订单数">{{ currentProduct.orders }}</el-descriptions-item>
          <el-descriptions-item label="利润率">
            <span :class="getRateClass(currentProduct.profitRate)">{{ currentProduct.profitRate }}%</span>
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <div class="product-actions">
          <el-button type="primary" @click="openInWB(currentProduct)">
            <el-icon><Link /></el-icon>
            在WB中查看
          </el-button>
          <el-button @click="editProduct(currentProduct)">
            <el-icon><Edit /></el-icon>
            编辑产品
          </el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import {
  Clock, Shop, User, ArrowDown, Check, Plus, Grid, Download, 
  Search, QuestionFilled, Close, ArrowRight, WarningFilled, Warning,
  Star, More, View, Edit, Money, PriceTag, Box, TrendCharts, Clock as ClockIcon,
  Link, CopyDocument, Document, Rank, Filter, OfficeBuilding, Setting
} from '@element-plus/icons-vue'

// ==================== 数据状态 ====================
const loading = ref(false)
const lastUpdateTime = ref('2026-03-26 14:00')
const products = ref([])
const shops = ref([])
const selectedProducts = ref([])
const productTableRef = ref(null)
const currentProduct = ref(null)
const showProductDetail = ref(false)

const filters = reactive({
  shopId: null,
  period: '7d',
  dateRange: null,
  search: ''
})

// 标签
const availableTags = ref(['新品', '促销', '滞销', '爆款', '清仓', '主推', '清货', 'test'])
const selectedTags = ref([])
const tagSearch = ref('')
const showCreateTag = ref(false)
const newTagName = ref('')
const tagDialogVisible = ref(false)
const editingProducts = ref([])
const selectedTagList = ref([])
const newTagInput = ref('')

// 指标配置
const allMetrics = ref([
  { key: 'sales', label: '销售额', enabled: true, order: 0, needValue: false, description: '总销售额', value: 1234567, subValue: '环比 +12.3%' },
  { key: 'orders', label: '订单数', enabled: true, order: 1, needValue: false, description: '总订单数', value: 856, subValue: '环比 +5.2%' },
  { key: 'profit', label: '利润', enabled: true, order: 2, needValue: false, description: '总利润', value: 234567, subValue: '利润率 19%' },
  { key: 'returnRate', label: '退货率', enabled: true, order: 3, needValue: true, filterType: 'gt', filterValue: 5, description: '退货率(%)', value: 23 },
  { key: 'stockOut', label: '低库存', enabled: true, order: 4, needValue: true, filterType: 'lt', filterValue: 10, description: '库存<10商品数', value: 12 },
  { key: 'noSales', label: '无销量', enabled: true, order: 5, needValue: true, filterType: 'eq', filterValue: 0, description: '无销量商品数', value: 45 },
  { key: 'lowProfit', label: '低利润', enabled: true, order: 6, needValue: true, filterType: 'lt', filterValue: 10, description: '利润率<10%商品', value: 28 },
  { key: 'avgPrice', label: '平均单价', enabled: false, order: 7, needValue: false, description: '商品平均单价', value: 1456 },
])

const activeMetrics = computed(() => 
  allMetrics.value.filter(m => m.enabled).sort((a, b) => a.order - b.order)
)

const showMetricSettings = ref(false)
const showMetricFilterDialog = ref(false)
const editingMetric = ref(null)

// 列配置
const allColumns = ref([
  { prop: 'nmId', label: 'NM_ID', visible: true, sortable: true, width: 100, filterHint: '按NM_ID筛选' },
  { prop: 'sku', label: 'SKU', visible: true, sortable: true, width: 130, filterHint: '按SKU筛选' },
  { prop: 'name', label: '产品名称', visible: true, sortable: true, minWidth: 200, filterHint: '按名称筛选' },
  { prop: 'price', label: '价格', visible: true, sortable: true, width: 100, align: 'right' },
  { prop: 'finalPrice', label: '最终价', visible: false, sortable: true, width: 100, align: 'right' },
  { prop: 'discount', label: '折扣', visible: false, sortable: true, width: 70 },
  { prop: 'stock', label: '库存', visible: true, sortable: true, width: 80, align: 'right', filterHint: '筛选低库存' },
  { prop: 'sales', label: '销售额', visible: true, sortable: true, width: 110, align: 'right' },
  { prop: 'orders', label: '订单数', visible: true, sortable: true, width: 80, align: 'right' },
  { prop: 'profitRate', label: '利润率', visible: true, sortable: true, width: 90, align: 'right', filterHint: '筛选低利润' },
  { prop: 'conversionRate', label: '转化率', visible: false, sortable: true, width: 90, align: 'right' },
  { prop: 'rating', label: '评分', visible: true, sortable: true, width: 100 },
  { prop: 'warehouse', label: '仓库', visible: true, sortable: false, width: 120 },
  { prop: 'tags', label: '标签', visible: true, sortable: false, minWidth: 180 },
  { prop: 'daysOnSite', label: '上架天数', visible: false, sortable: true, width: 90 },
  { prop: 'actions', label: '', visible: true, sortable: false, width: 50, fixed: 'right' },
])

const visibleColumns = computed(() => allColumns.value.filter(col => col.visible))

// 角色
const roles = ref([
  { id: 'default', name: '默认视图', description: '系统默认视图' },
  { id: 'finance', name: '财务分析', description: '专注财务指标' },
  { id: 'inventory', name: '库存监控', description: '专注库存状态' },
])
const currentRole = ref(roles.value[0])
const showRoleDialog = ref(false)
const editingRole = ref(null)
const roleDialogTitle = ref('')

// 仓库
const showWarehouseDetail = ref(false)

// 分页
const pagination = reactive({ page: 1, pageSize: 50 })

// 快速筛选
const activeQuickFilter = ref(null)
const quickFilters = ref([
  { key: 'lowStock', label: '低库存', count: 12, type: 'warning' },
  { key: 'lowProfit', label: '低利润', count: 8, type: 'danger' },
  { key: 'highReturn', label: '高退货', count: 5, type: 'danger' },
  { key: 'noSales', label: '无销量', count: 23, type: 'info' },
])

// 拖拽
let draggedMetricIdx = null

// ==================== 计算属性 ====================
const filteredAvailableTags = computed(() => {
  if (!tagSearch.value) return availableTags.value
  return availableTags.value.filter(t => t.toLowerCase().includes(tagSearch.value.toLowerCase()))
})

const filteredProducts = computed(() => {
  let result = [...products.value]
  
  if (filters.shopId) result = result.filter(p => p.shopId === filters.shopId)
  
  if (selectedTags.value.length > 0) {
    result = result.filter(p => p.tags && selectedTags.value.some(t => p.tags.includes(t)))
  }
  
  if (filters.search) {
    const s = filters.search.toLowerCase()
    result = result.filter(p => 
      p.name?.toLowerCase().includes(s) ||
      p.sku?.toLowerCase().includes(s)
      || p.nmId?.toString().includes(s)
    )
  }
  
  if (activeQuickFilter.value) {
    const qf = quickFilters.value.find(q => q.key === activeQuickFilter.value)
    if (qf) {
      if (qf.key === 'lowStock') result = result.filter(p => p.stock < 10)
      else if (qf.key === 'lowProfit') result = result.filter(p => parseFloat(p.profitRate) < 10)
      else if (qf.key === 'noSales') result = result.filter(p => p.orders === 0)
    }
  }
  
  activeMetrics.value.forEach(metric => {
    if (metric.active && metric.filterValue !== undefined) {
      result = result.filter(p => {
        const val = parseFloat(p[metric.key]) || 0
        if (metric.filterType === 'lt') return val < metric.filterValue
        if (metric.filterType === 'gt') return val > metric.filterValue
        if (metric.filterType === 'eq') return val === metric.filterValue
        return true
      })
    }
  })
  
  return result
})

const displayProducts = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  return filteredProducts.value.slice(start, start + pagination.pageSize)
})

const selectedSalesTotal = computed(() => selectedProducts.value.reduce((sum, p) => sum + (parseFloat(p.sales) || 0), 0))
const selectedOrdersTotal = computed(() => selectedProducts.value.reduce((sum, p) => sum + (parseInt(p.orders) || 0), 0))
const selectedProfitTotal = computed(() => selectedProducts.value.reduce((sum, p) => sum + ((parseFloat(p.sales) || 0) * parseFloat(p.profitRate || 0) / 100), 0))

const warehouseDetailList = computed(() => {
  const map = {}
  products.value.forEach(p => {
    if (p.warehouseDetail) {
      Object.entries(p.warehouseDetail).forEach(([wh, qty]) => {
        map[wh] = (map[wh] || 0) + qty
      })
    }
  })
  const total = Object.values(map).reduce((s, v) => s + v, 0)
  return Object.entries(map).map(([warehouse, quantity]) => ({
    warehouse,
    quantity,
    percent: total > 0 ? ((quantity / total) * 100).toFixed(1) + '%' : '0%'
  }))
})

// ==================== 方法 ====================
async function fetchShops() {
  try {
    const response = await axios.get('/api/shops/')
    shops.value = response.data
    if (shops.value.length > 0) filters.shopId = shops.value[0].id
  } catch (error) { console.error('获取店铺失败', error) }
}

async function fetchData() {
  loading.value = true
  try {
    products.value = generateMockData()
    lastUpdateTime.value = new Date().toLocaleString('zh-CN')
  } catch (error) { ElMessage.error('获取数据失败') } finally { loading.value = false }
}

function generateMockData() {
  const mock = []
  const names = ['无线蓝牙耳机 Pro Max', 'iPhone 15手机壳 透白', '20000mAh 移动电源', '智能运动手表 GPS', '男士运动鞋 缓震跑步', '女装轻薄外套 防风', '男士纯棉T恤 基础款', '儿童益智积木 500pcs', '厨房多功能切菜器', '家用投影仪 4K智能', '宠物自动饮水机', '女士斜挎包 小CK质感']
  const tags = ['新品', '促销', '滞销', '爆款', '清仓', '主推', '清货']
  const warehouses = ['莫斯科', '圣彼得堡', '新西伯利亚', '叶卡捷琳堡']
  
  for (let i = 1; i <= 200; i++) {
    const productTags = []
    const tagCount = Math.floor(Math.random() * 3)
    for (let j = 0; j < tagCount; j++) {
      const tag = tags[Math.floor(Math.random() * tags.length)]
      if (!productTags.includes(tag)) productTags.push(tag)
    }
    const warehouse = warehouses[Math.floor(Math.random() * warehouses.length)]
    const price = Math.random() * 5000 + 500
    const stock = Math.floor(Math.random() * 300)
    const sales = Math.floor(Math.random() * 10000)
    const conversionRate = (Math.random() * 10 + 1).toFixed(2)
    
    mock.push({
      id: i, nmId: 100000 + Math.floor(Math.random() * 900000),
      sku: 'SKU' + String(i).padStart(6, '0'),
      name: names[Math.floor(Math.random() * names.length)] + ' #' + i,
      price: price.toFixed(2), finalPrice: (price * 0.85).toFixed(2),
      discount: Math.floor(Math.random() * 30 + 5), stock, sales,
      orders: Math.floor(sales / (price * 0.85)),
      profitRate: (Math.random() * 35 + 5).toFixed(1),
      conversionRate, rating: (Math.random() * 2 + 3.5).toFixed(1),
      ratingCount: Math.floor(Math.random() * 500),
      warehouse, warehouseDetail: { [warehouse]: stock, '其他仓库': Math.floor(Math.random() * 50) },
      tags: productTags, daysOnSite: Math.floor(Math.random() * 365),
      shopId: Math.floor(Math.random() * 3) + 1
    })
  }
  return mock
}

function selectShop(id) { filters.shopId = id; pagination.page = 1; fetchData() }
function handlePeriodChange() { if (filters.period !== 'custom') { pagination.page = 1; fetchData() } }
function refreshData() { fetchData(); ElMessage.success('数据已刷新') }
function handleSearch() { clearTimeout(window.searchTimer); window.searchTimer = setTimeout(() => { pagination.page = 1 }, 300) }

function handleTagFilterChange() { pagination.page = 1 }

function toggleQuickFilter(filter) {
  if (activeQuickFilter.value === filter.key) activeQuickFilter.value = null
  else activeQuickFilter.value = filter.key
}

function toggleMetricFilter(metric) {
  if (!metric.needValue) { metric.active = !metric.active; return }
  editingMetric.value = { ...metric }
  showMetricFilterDialog.value = true
}

function clearMetricFilter(metric) { metric.active = false }

function applyMetricFilter() {
  if (editingMetric.value) {
    const m = allMetrics.value.find(x => x.key === editingMetric.value.key)
    if (m) { m.active = true; m.filterType = editingMetric.value.filterType; m.filterValue = editingMetric.value.filterValue }
  }
  showMetricFilterDialog.value = false
}

function onMetricDragStart(e, idx) { draggedMetricIdx = idx }
function onMetricDrop(idx) {
  if (draggedMetricIdx !== null && draggedMetricIdx !== idx) {
    const metrics = allMetrics.value.filter(m => m.enabled)
    const [removed] = metrics.splice(draggedMetricIdx, 1)
    metrics.splice(idx, 0, removed)
    metrics.forEach((m, i) => m.order = i)
  }
  draggedMetricIdx = null
}

function handleColumnHeaderClick(col) { if (col.filterHint) ElMessage.info('筛选功能: ' + col.filterHint) }

function handleSelectionChange(selection) { selectedProducts.value = selection }
function handleSortChange({ prop, order }) { if (!prop || !order) return; const mul = order === 'ascending' ? 1 : -1; products.value.sort((a, b) => (parseFloat(a[prop]) || 0) - (parseFloat(b[prop]) || 0) * mul) }
function handleRowClick(row) {}
function handleRowDblClick(row) { currentProduct.value = row; showProductDetail.value = true }
function getRowClassName({ row }) { return selectedProducts.value.some(p => p.id === row.id) ? 'selected-row' : '' }
function getColumnClassName(prop) { return prop === 'actions' ? 'actions-column' : '' }
function checkSelectable() { return true }
function cellSpanMethod() {}

function startCellSelection() {}
function extendCellSelection() {}
function endCellSelection() {}

function handleRoleCommand(cmd) {
  if (cmd === 'createRole') { editingRole.value = { id: Date.now().toString(), name: '', description: '' }; roleDialogTitle.value = '创建新角色'; showRoleDialog.value = true }
  else if (cmd === 'manageRole') { editingRole.value = { ...currentRole.value }; roleDialogTitle.value = '编辑角色'; showRoleDialog.value = true }
  else if (cmd.startsWith('role:')) { const id = cmd.split(':')[1]; const role = roles.value.find(r => r.id === id); if (role) currentRole.value = role }
}

function saveRole() { if (!editingRole.value.name) { ElMessage.warning('请输入角色名称'); return } const idx = roles.value.findIndex(r => r.id === editingRole.value.id); if (idx >= 0) roles.value[idx] = { ...editingRole.value }; else roles.value.push({ ...editingRole.value }); ElMessage.success('保存成功'); showRoleDialog.value = false }

function deleteRole() { ElMessageBox.confirm('确定要删除这个角色吗？', '提示', { type: 'warning' }).then(() => { roles.value = roles.value.filter(r => r.id !== editingRole.value.id); currentRole.value = roles.value[0]; ElMessage.success('已删除'); showRoleDialog.value = false }).catch(() => {}) }

function handleViewCommand(cmd) { if (cmd === 'saveView') ElMessage.info('请选择角色保存当前视图') }

function resetColumns() { allColumns.value.forEach(col => col.visible = true); saveColumnSettings() }
function saveColumnSettings() { localStorage.setItem('productColumnSettings', JSON.stringify(allColumns.value)) }
function saveMetricSettings() { localStorage.setItem('productMetricSettings', JSON.stringify(allMetrics.value)) }

function handleExportCommand(cmd) { ElMessage.info('导出 ' + cmd + ' 功能开发中') }

function handleBatchCommand(cmd) {
  if (selectedProducts.value.length === 0) { ElMessage.warning('请先选择产品'); return }
  if (cmd === 'batchTag') openTagDialog(selectedProducts.value)
  else ElMessage.info(cmd + ' 功能开发中')
}

function openTagDialog(products) { editingProducts.value = products; selectedTagList.value = [...(products[0]?.tags || [])]; tagDialogVisible.value = true }

function addNewTag() { if (newTagInput.value && !availableTags.value.includes(newTagInput.value)) { availableTags.value.push(newTagInput.value); selectedTagList.value.push(newTagInput.value); newTagInput.value = '' } }

function saveProductTags() { editingProducts.value.forEach(p => { p.tags = [...selectedTagList.value] }); ElMessage.success('标签已保存'); tagDialogVisible.value = false }

function confirmCreateTag() { if (newTagName.value && !availableTags.value.includes(newTagName.value)) { availableTags.value.push(newTagName.value); ElMessage.success('标签已创建') } showCreateTag.value = false; newTagName.value = '' }

function handleProductAction(cmd, row) {
  switch (cmd) {
    case 'detail': currentProduct.value = row; showProductDetail.value = true; break
    case 'edit': ElMessage.info('编辑 ' + row.name); break
    case 'cost': ElMessage.info('编辑成本'); break
    case 'price': ElMessage.info('编辑价格'); break
    case 'supply': ElMessage.info('供应链计算'); break
    case 'ad': ElMessage.info('查看广告'); break
    case 'history': ElMessage.info('历史走势'); break
    case 'source': window.open('https://www.wildberries.ru/catalog/' + row.nmId + '/detail.aspx', '_blank'); break
    case 'copy': navigator.clipboard.writeText('https://www.wildberries.ru/catalog/' + row.nmId + '/detail.aspx'); ElMessage.success('链接已复制'); break
  }
}

function filterByWarehouse(row) { filters.warehouse = row.warehouse; showWarehouseDetail.value = false; ElMessage.info('已筛选仓库: ' + row.warehouse) }
function openInWB(product) { window.open('https://www.wildberries.ru/catalog/' + product.nmId + '/detail.aspx', '_blank') }
function editProduct(product) { ElMessage.info('编辑产品: ' + product.name) }

function getRateClass(rate) { const r = parseFloat(rate); if (r < 10) return 'rate-danger'; if (r < 20) return 'rate-warning'; return 'rate-success' }
function formatNumber(num) { return num.toLocaleString('ru-RU', { maximumFractionDigits: 0 }) }
function formatPrice(price) { return parseFloat(price || 0).toLocaleString('ru-RU', { maximumFractionDigits: 2 }) }

function handleSizeChange() { pagination.page = 1 }
function handlePageChange() {}

onMounted(() => { fetchShops(); fetchData() })
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



.product-analysis { height: 100vh; overflow: hidden; background: #f5f7fa; }
.analysis-layout { display: flex; height: 100%; }
.left-sidebar { width: 220px; background: #fff; border-right: 1px solid #e4e7ed; display: flex; flex-direction: column; overflow-y: auto; }
.sidebar-header { padding: 16px; font-weight: 600; border-bottom: 1px solid #e4e7ed; }
.shop-list { padding: 8px; }
.shop-item { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
.shop-item:hover { background: #f5f7fa; }
.shop-item.active { background: #ecfdf5; color: #10b981; }
.shop-name { flex: 1; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.quick-filters, .tags-filter-section { padding: 12px; }
.filter-section-title { font-size: 12px; color: #909399; margin-bottom: 8px; text-transform: uppercase; }
.quick-filter-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; }
.quick-filter-item:hover { background: #f5f7fa; }
.quick-filter-item.active { background: #ecfdf5; color: #10b981; }
.main-content { flex: 1; display: flex; flex-direction: column; overflow: hidden; padding: 16px; }
.top-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.update-info { font-size: 12px; color: #909399; display: flex; align-items: center; gap: 6px; }
.metrics-panel { background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
.metrics-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.metrics-title { font-weight: 600; font-size: 14px; }
.metrics-grid { display: flex; gap: 12px; flex-wrap: wrap; overflow-x: auto; }
.metric-card { background: #f9fafb; border: 2px solid transparent; border-radius: 8px; padding: 12px 16px; min-width: 130px; max-width: 180px; cursor: pointer; transition: all 0.2s; position: relative; }
.metric-card:hover { border-color: #d1d5db; }
.metric-card.active { border-color: #10b981; background: #ecfdf5; }
.metric-card.warning.active { border-color: #f59e0b; background: #fffbeb; }
.metric-card.danger.active { border-color: #ef4444; background: #fef2f2; }
.metric-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.metric-label { font-size: 12px; color: #6b7280; }
.metric-help { color: #9ca3af; font-size: 12px; }
.metric-value { font-size: 22px; font-weight: 700; color: #111827; }
.metric-sub { font-size: 11px; color: #10b981; margin-top: 2px; }
.metric-filter-info { font-size: 11px; color: #ef4444; margin-top: 4px; display: flex; align-items: center; gap: 4px; }
.filter-clear { cursor: pointer; }
.metric-drag-handle { position: absolute; top: 8px; right: 8px; cursor: grab; opacity: 0; transition: opacity 0.2s; }
.metric-card:hover .metric-drag-handle { opacity: 1; }
.table-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; background: #fff; padding: 12px 16px; border-radius: 8px; }
.table-container { flex: 1; background: #fff; border-radius: 8px; overflow: auto; margin-bottom: 16px; }
.table-footer { display: flex; justify-content: space-between; align-items: center; background: #fff; padding: 12px 16px; border-radius: 8px; font-size: 13px; color: #606266; }
.footer-stats { display: flex; gap: 16px; }
.stat-item { margin-left: 12px; }
.stat-item strong { color: #303133; }
.tags-cell { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; }
.warehouse-link { color: #409eff; cursor: pointer; display: flex; align-items: center; gap: 2px; }
.warehouse-detail-popover { padding: 8px 0; }
.warehouse-detail-title { font-weight: 600; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #eee; }
.warehouse-row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 13px; }
.wh-name { color: #606266; }
.wh-qty { font-weight: 500; }
.warehouse-footer { margin-top: 8px; padding-top: 8px; border-top: 1px solid #eee; text-align: center; }
.low-stock { color: #f59e0b; }
.out-of-stock { color: #ef4444; font-weight: 600; }
.rate-danger { color: #ef4444; font-weight: 600; }
.rate-warning { color: #f59e0b; font-weight: 600; }
.rate-success { color: #10b981; font-weight: 600; }
.rating-cell { display: flex; align-items: center; gap: 2px; }
.rating-count { color: #909399; font-size: 12px; margin-left: 4px; }
.sales-cell { font-weight: 500; }
.discount-badge { background: #fef2f2; color: #ef4444; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
.column-header { display: flex; align-items: center; gap: 4px; }
.filter-hint { color: #c0c4cc; font-size: 12px; cursor: help; }
.filter-type-group { display: flex; gap: 12px; }
.metric-settings-info { margin-bottom: 16px; padding: 12px; background: #f5f7fa; border-radius: 6px; font-size: 13px; color: #606266; }
.metric-settings-list { display: flex; flex-direction: column; gap: 12px; }
.metric-setting-item { display: flex; align-items: center; gap: 12px; }
.metric-setting-desc { font-size: 12px; color: #909399; }
.tag-edit-info { margin-bottom: 16px; padding: 12px; background: #f5f7fa; border-radius: 6px; font-size: 13px; }
.product-actions { display: flex; gap: 12px; }
:deep(.el-table .selected-row) { background: #ecfdf5 !important; }
:deep(.el-table .actions-column) { padding: 0 8px !important; }
</style>
