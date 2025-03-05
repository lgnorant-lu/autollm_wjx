import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/animations.css'

// Element Plus 图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// ECharts相关导入
import * as echarts from 'echarts'
import VueECharts from 'vue-echarts'

const app = createApp(App)

// 全局注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局注册 ECharts 组件
app.component('v-chart', VueECharts)

app.use(router)
app.use(ElementPlus)
app.mount('#app')