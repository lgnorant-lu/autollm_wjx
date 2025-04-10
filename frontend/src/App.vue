<template>
  <el-container class="layout-container" style="min-height: 100vh;">
    <!-- 侧边栏 -->
    <el-aside width="200px">
      <el-menu
        :router="true"
        default-active="/"
        class="el-menu-vertical"
        :background-color="isDark ? '#1a1a1a' : '#545c64'"
        :text-color="isDark ? '#e0e0e0' : '#fff'"
        :active-text-color="isDark ? '#ffa117' : '#ffd04b'"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/surveys">
          <el-icon><Document /></el-icon>
          <span>问卷管理</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><Tickets /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <!-- 顶部栏 -->
      <el-header>
        <div class="header-content">
          <div class="header-title">问卷星自动化系统</div>
          <ThemeSwitch v-model="isDark" @update:isDark="updateTheme" />
        </div>
      </el-header>
      
      <!-- 主要内容区 -->
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
      
      <!-- 底部 -->
      <el-footer>
        <div class="footer-text">问卷星自动化系统 2025</div>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { House, Document, Tickets, Setting } from '@element-plus/icons-vue'
import ThemeSwitch from './components/ThemeSwitch.vue'

// 主题状态
const isDark = ref(false)

// 从本地存储中获取主题
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
  }
})

// 更新主题
const updateTheme = (darkMode) => {
  isDark.value = darkMode
}
</script>

<style>
:root {
  --primary-bg: #ffffff;
  --primary-text: #333333;
  --secondary-bg: #f5f7fa;
  --hover-color: #6e5af0;
}

:root[data-theme='dark'] {
  --primary-bg: #1a1a1a;
  --primary-text: #ffffff;
  --secondary-bg: #2d2d2d;
  --hover-color: #ffa117;
}

.layout-container {
  height: 100vh;
  background: var(--primary-bg);
  color: var(--primary-text);
}

.el-menu-vertical {
  height: 100%;
  border-right: none;
}

.el-header {
  background-color: var(--el-color-primary);
  padding: 0 20px;
}

.header-content {
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  color: white;
  font-size: 20px;
  font-weight: bold;
}

.el-main {
  background-color: var(--secondary-bg);
  padding: 20px;
}

.el-footer {
  background-color: var(--primary-bg);
  text-align: center;
  line-height: 60px;
  color: var(--primary-text);
  border-top: 1px solid var(--el-border-color-light);
}

/* 页面切换动画 */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>