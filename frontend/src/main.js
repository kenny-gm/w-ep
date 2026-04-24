import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './styles/index.css'
import './styles/glassmorphism.css'
import axios from 'axios'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())

// 添加axios请求拦截器
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem("token") || localStorage.getItem("access_token") || ""
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

app.use(router)
app.use(ElementPlus)

app.mount('#app')
