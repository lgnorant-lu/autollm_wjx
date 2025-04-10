<template>
  <div class="theme-switch">
    <div class="theme-toggle" @click="toggleTheme" :class="{ 'dark-mode': isDark }">
      <div class="theme-toggle-track">
        <div class="theme-toggle-track-sun">
          <span class="icon-sun"></span>
        </div>
        <div class="theme-toggle-track-moon">
          <span class="icon-moon"></span>
        </div>
      </div>
      <div class="theme-toggle-thumb"></div>
      <input class="theme-toggle-screenreader-only" type="checkbox" aria-label="Dark mode toggle" v-model="isDark">
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const emit = defineEmits(['update:isDark'])
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const isDark = ref(props.modelValue)

// When isDark changes, emit the update
watch(isDark, (newValue) => {
  emit('update:isDark', newValue)
})

// 检查用户以前的主题选择
onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    applyTheme(true)
    emit('update:isDark', true)
  }
})

const toggleTheme = () => {
  isDark.value = !isDark.value
  applyTheme(isDark.value)
  // 保存用户选择
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

const applyTheme = (isDarkMode) => {
  // 切换主题色
  document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light')
  
  // 更新CSS变量
  document.documentElement.style.setProperty('--primary-bg', isDarkMode ? '#1a1a1a' : '#ffffff')
  document.documentElement.style.setProperty('--primary-text', isDarkMode ? '#ffffff' : '#333333')
  document.documentElement.style.setProperty('--secondary-bg', isDarkMode ? '#2d2d2d' : '#f5f7fa')
  document.documentElement.style.setProperty('--hover-color', isDarkMode ? '#ffa117' : '#6e5af0')
  
  // 添加平滑过渡效果
  document.body.classList.add('theme-transition')
  setTimeout(() => {
    document.body.classList.remove('theme-transition')
  }, 1000)
}
</script>

<style>
:root {
  --primary-bg: #ffffff;
  --primary-text: #333333;
  --secondary-bg: #f5f7fa;
  --hover-color: #6e5af0;
}

.theme-switch {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

/* Theme transition effects */
.theme-transition {
  transition: background-color 0.5s ease, color 0.5s ease;
}

.theme-transition * {
  transition: background-color 0.5s ease, border-color 0.5s ease, color 0.5s ease, box-shadow 0.5s ease !important;
}

/* Animated toggle switch */
.theme-toggle {
  position: relative;
  display: inline-block;
  height: 34px;
  width: 74px;
  cursor: pointer;
}

.theme-toggle-track {
  background-color: #4d4d4d;
  border-radius: 34px;
  box-shadow: 0 0 2px 2px rgba(0, 0, 0, 0.05);
  height: 100%;
  overflow: hidden;
  position: relative;
  width: 100%;
}

.theme-toggle-track-sun, 
.theme-toggle-track-moon {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: transform 0.5s cubic-bezier(0.23, 1, 0.32, 1);
}

.theme-toggle-track-sun {
  left: 2px;
}

.theme-toggle-track-moon {
  right: 2px;
}

.theme-toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 30px;
  height: 30px;
  background-color: white;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.3);
  transition: transform 0.5s cubic-bezier(0.23, 1, 0.32, 1);
}

.theme-toggle.dark-mode .theme-toggle-thumb {
  transform: translateX(40px);
}

.theme-toggle-screenreader-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Icons */
.icon-sun, .icon-moon {
  display: inline-block;
  height: 16px;
  width: 16px;
}

.icon-sun {
  background: radial-gradient(circle, rgba(255,255,255,1) 0%, rgba(255,255,255,0) 70%);
  box-shadow: 0 0 10px 2px rgba(255, 255, 255, 0.6);
}

.icon-moon {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  box-shadow: inset -3px 1px 0 rgba(0, 0, 0, 0.2);
}

/* Dark mode styles for the toggle */
.theme-toggle.dark-mode .theme-toggle-track {
  background-color: #2d2d2d;
}
</style>