<template>
  <div class="product-sales-demo">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>📦 产品销售明细</h2>
      <p class="subtitle">以产品为核心，查看各店铺销售数据</p>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-item">
        <span>时间范围</span>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始"
          end-placeholder="结束"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 240px"
        />
      </div>
      <div class="filter-item">
        <span>产品</span>
        <el-select v-model="selectedProduct" placeholder="全部产品" style="width: 200px" filterable>
          <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>
      <div class="filter-item">
        <el-button type="primary">查询</el-button>
      </div>
    </div>

    <!-- 产品销售表格 -->
    <div class="table-container">
      <table class="product-table">
        <thead>
          <tr>
            <th class="product-col">产品名称</th>
            <th class="sku-col">SKU</th>
            <th v-for="shop in shops" :key="shop.id" class="shop-col">
              <div class="shop-header">
                <span class="shop-name">{{ shop.name }}</span>
                <span class="shop-currency">{{ shop.currency }}</span>
              </div>
              <div class="metrics-header">
                <span>访客</span>
                <span>加购</span>
                <span>订单</span>
                <span>销售额</span>
              </div>
            </th>
            <th class="total-col">合计</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in productData" :key="product.id" class="product-row">
            <td class="product-col">
              <div class="product-name">{{ product.name }}</div>
            </td>
            <td class="sku-col">
              <span class="sku">{{ product.sku }}</span>
            </td>
            <td v-for="shop in shops" :key="shop.id" class="shop-col">
              <div class="shop-data">
                <span class="metric visitors">{{ formatNumber(product.shopData[shop.id]?.visitors || 0) }}</span>
                <span class="metric cart">{{ formatNumber(product.shopData[shop.id]?.cart || 0) }}</span>
                <span class="metric orders">{{ formatNumber(product.shopData[shop.id]?.orders || 0) }}</span>
                <span class="metric sales">{{ formatCurrency(product.shopData[shop.id]?.sales || 0, shop.currency) }}</span>
              </div>
            </td>
            <td class="total-col">
              <div class="total-data">
                <span class="metric visitors">{{ formatNumber(product.total.visitors) }}</span>
                <span class="metric cart">{{ formatNumber(product.total.cart) }}</span>
                <span class="metric orders">{{ formatNumber(product.total.orders) }}</span>
                <span class="metric sales">{{ formatCurrency(product.total.sales, 'RUB') }}</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 数据说明 -->
    <div class="info-box">
      <p>💡 <strong>设计说明：</strong></p>
      <ul>
        <li>以产品名称为主键，不同店铺的数据横向展示</li>
        <li>每个店铺下显示：访客数、加购数、订单数、销售额</li>
        <li>右侧自动计算所有店铺的合计</li>
        <li>支持按产品筛选时间范围筛选</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const dateRange = ref(['2026-04-01', '2026-04-15'])
const selectedProduct = ref(null)

const shops = ref([
  { id: 1, name: '炊恒跨境1', currency: 'CNY' },
  { id: 2, name: '炊恒跨境2', currency: 'CNY' },
  { id: 3, name: '俄罗斯店铺A', currency: 'RUB' },
])

const products = ref([
  { id: 1, name: '无线蓝牙耳机 Pro Max', sku: 'WB001' },
  { id: 2, name: 'iPhone 15手机壳 透白', sku: 'WB002' },
  { id: 3, name: '20000mAh 移动电源', sku: 'WB003' },
  { id: 4, name: '智能运动手表 GPS', sku: 'WB004' },
  { id: 5, name: '男士运动鞋 缓震跑步', sku: 'WB005' },
])

// 模拟数据
const productData = ref([
  {
    id: 1,
    name: '无线蓝牙耳机 Pro Max',
    sku: 'WB001',
    shopData: {
      1: { visitors: 1234, cart: 89, orders: 45, sales: 89500 },
      2: { visitors: 2345, cart: 156, orders: 78, sales: 156000 },
      3: { visitors: 567, cart: 34, orders: 18, sales: 45000 },
    },
    total: { visitors: 4146, cart: 279, orders: 141, sales: 290500 }
  },
  {
    id: 2,
    name: 'iPhone 15手机壳 透白',
    sku: 'WB002',
    shopData: {
      1: { visitors: 890, cart: 67, orders: 34, sales: 6780 },
      2: { visitors: 1567, cart: 123, orders: 56, sales: 11200 },
      3: { visitors: 0, cart: 0, orders: 0, sales: 0 },
    },
    total: { visitors: 2457, cart: 190, orders: 90, sales: 17980 }
  },
  {
    id: 3,
    name: '20000mAh 移动电源',
    sku: 'WB003',
    shopData: {
      1: { visitors: 3456, cart: 234, orders: 123, sales: 184500 },
      2: { visitors: 0, cart: 0, orders: 0, sales: 0 },
      3: { visitors: 789, cart: 45, orders: 23, sales: 34500 },
    },
    total: { visitors: 4245, cart: 279, orders: 146, sales: 219000 }
  },
  {
    id: 4,
    name: '智能运动手表 GPS',
    sku: 'WB004',
    shopData: {
      1: { visitors: 0, cart: 0, orders: 0, sales: 0 },
      2: { visitors: 4567, cart: 345, orders: 178, sales: 356000 },
      3: { visitors: 1234, cart: 89, orders: 45, sales: 90000 },
    },
    total: { visitors: 5801, cart: 434, orders: 223, sales: 446000 }
  },
  {
    id: 5,
    name: '男士运动鞋 缓震跑步',
    sku: 'WB005',
    shopData: {
      1: { visitors: 678, cart: 45, orders: 23, sales: 46000 },
      2: { visitors: 1234, cart: 78, orders: 39, sales: 78000 },
      3: { visitors: 456, cart: 28, orders: 14, sales: 28000 },
    },
    total: { visitors: 2368, cart: 151, orders: 76, sales: 152000 }
  },
])

function formatNumber(num) {
  if (num >= 1000) {
    return num.toLocaleString('zh-CN')
  }
  return num
}

function formatCurrency(amount, currency) {
  if (currency === 'CNY') {
    return '¥' + formatNumber(amount)
  }
  return formatNumber(amount) + ' ₽'
}
</script>

<style scoped>
.product-sales-demo {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  color: #909399;
  margin: 0;
  font-size: 14px;
}

.filter-bar {
  display: flex;
  gap: 20px;
  background: white;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-item span {
  color: #606266;
  font-size: 14px;
  white-space: nowrap;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow-x: auto;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.product-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  min-width: 800px;
}

.product-table th,
.product-table td {
  padding: 12px 16px;
  text-align: center;
  border-bottom: 1px solid #ebeef5;
}

.product-table th {
  background: #fafafa;
  font-weight: 600;
  color: #606266;
  position: sticky;
  top: 0;
  z-index: 10;
}

.product-col {
  text-align: left !important;
  min-width: 200px;
}

.sku-col {
  min-width: 80px;
}

.sku {
  font-family: monospace;
  color: #909399;
  font-size: 12px;
}

.shop-col {
  min-width: 140px;
  background: #fafafa;
}

.shop-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.shop-name {
  font-weight: 600;
  color: #303133;
  font-size: 13px;
}

.shop-currency {
  font-size: 11px;
  color: #909399;
}

.metrics-header {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  font-size: 11px;
  color: #909399;
}

.product-row:hover {
  background: #f5f7fa;
}

.product-name {
  font-weight: 500;
  color: #303133;
}

.shop-data,
.total-data {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  font-size: 12px;
}

.metric {
  padding: 4px 2px;
  border-radius: 4px;
}

.metric.visitors {
  color: #409eff;
}

.metric.cart {
  color: #8b5cf6;
}

.metric.orders {
  color: #f97316;
}

.metric.sales {
  color: #10b981;
  font-weight: 500;
}

.total-col {
  background: #eef2ff;
  min-width: 120px;
}

.total-col .total-data {
  font-weight: 600;
}

.total-col .metric.sales {
  color: #10b981;
  font-weight: 700;
}

.info-box {
  margin-top: 20px;
  padding: 16px 20px;
  background: #f0f9eb;
  border-radius: 8px;
  border-left: 4px solid #67c23a;
}

.info-box p {
  margin: 0 0 8px 0;
  color: #606266;
}

.info-box ul {
  margin: 0;
  padding-left: 20px;
  color: #909399;
  font-size: 13px;
}

.info-box li {
  margin-bottom: 4px;
}

/* 响应式 */
@media (max-width: 768px) {
  .product-sales-demo {
    padding: 12px;
  }
  
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .filter-item {
    width: 100%;
  }
  
  .filter-item :deep(.el-select),
  .filter-item :deep(.el-date-editor) {
    width: 100% !important;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .product-table {
    font-size: 11px;
  }
  
  .product-table th,
  .product-table td {
    padding: 8px 6px;
  }
}
</style>
