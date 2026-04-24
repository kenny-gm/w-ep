import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '销售看板' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('../views/Inventory.vue'),
        meta: { title: '库存管理' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('../views/Orders.vue'),
        meta: { title: '订单管理' }
      },
      {
        path: 'ads',
        name: 'Ads',
        component: () => import('../views/AdAnalysis.vue'),
        meta: { title: '广告分析' }
      },
      {
        path: 'keyword-daily/:product_id',
        name: 'KeywordDailyDetail',
        component: () => import('../views/ad/KeywordDailyDetail.vue'),
        meta: { title: '关键词每日明细' }
      },
      {
        path: 'finance',
        name: 'Finance',
        component: () => import('../views/Finance.vue'),
        meta: { title: '利润分析' }
      },
      {
        path: 'alerts',
        name: 'Alerts',
        component: () => import('../views/admin/Alerts.vue'),
        meta: { title: '预警中心' }
      },
      {
        path: 'operation-logs',
        name: 'OperationLogs',
        component: () => import('../views/admin/OperationLogs.vue'),
        meta: { title: '运营日志' }
      },
      {
        path: 'product-sales',
        name: 'ProductSales',
        component: () => import('../views/ProductSalesDemo.vue'),
        meta: { title: '产品销售明细' }
      },
      // 后台管理路由
      {
        path: 'admin',
        name: 'Admin',
        component: () => import('../views/admin/AdminLayout.vue'),
        meta: { title: '后台管理', requiresAdmin: true },
        children: [
          {
            path: '',
            redirect: '/admin/users'
          },
          {
            path: 'users',
            name: 'AdminUsers',
            component: () => import('../views/admin/Users.vue'),
            meta: { title: '用户管理' }
          },
          {
            path: 'products',
            name: 'AdminProducts',
            component: () => import('../views/admin/Products.vue'),
            meta: { title: '产品管理' }
          },
          {
            path: 'shops',
            name: 'AdminShops',
            component: () => import('../views/admin/Shops.vue'),
            meta: { title: '店铺管理' }
          },
          {
            path: 'ui',
            name: 'AdminUI',
            component: () => import('../views/admin/UISettings.vue'),
            meta: { title: '界面管理' }
          },
          {
            path: 'menus',
            name: 'AdminMenus',
            component: () => import('../views/admin/MenuSettings.vue'),
            meta: { title: '菜单管理' }
          },
          {
            path: 'settings',
            name: 'AdminSettings',
            component: () => import('../views/admin/Settings.vue'),
            meta: { title: '系统设置' }
          },
          {
            path: 'thresholds',
            name: 'MetricThresholds',
            component: () => import('../views/admin/MetricThresholds.vue'),
            meta: { title: '预警阈值' }
          }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
