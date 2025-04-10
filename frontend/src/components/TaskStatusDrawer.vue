<template>
  <div class="task-status-drawer">
    <el-drawer
      v-model="drawerVisible"
      title="当前任务状态"
      direction="rtl"
      size="300px"
      :before-close="handleClose"
      :destroy-on-close="false"
    >
      <div class="active-task-container" v-if="activeTask">
        <div class="drawer-header">
          <el-tag :type="getStatusType(activeTask.status)" effect="dark" class="status-tag">
            {{ formatStatus(activeTask.status) }}
          </el-tag>
          <div class="task-time">{{ formatTime(activeTask.updated_at) }}</div>
        </div>
        
        <div class="progress-container">
          <div class="progress-header">
            <span>任务进度</span>
            <span class="progress-percentage">{{ calculateProgress(activeTask) }}%</span>
          </div>
          <el-progress 
            :percentage="calculateProgress(activeTask)" 
            :status="getProgressStatus(activeTask.status)" 
            :format="formatProgress"
            :stroke-width="10"
          />
        </div>
        
        <el-descriptions :column="1" border size="small" class="task-info">
          <el-descriptions-item label="任务ID">
            <el-tooltip :content="activeTask.id" placement="top">
              <span class="task-id">{{ activeTask.id ? activeTask.id.substring(0, 8) + '...' : 'N/A' }}</span>
            </el-tooltip>
          </el-descriptions-item>
          <el-descriptions-item label="问卷">
            {{ surveyTitle }}
          </el-descriptions-item>
          <el-descriptions-item label="计划提交">
            {{ activeTask.count || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="已完成">
            <el-row>
              <el-col :span="12">
                <el-statistic :value="activeTask.success_count || 0" title="成功">
                  <template #suffix>
                    <el-icon style="color: #67C23A"><Check /></el-icon>
                  </template>
                </el-statistic>
              </el-col>
              <el-col :span="12">
                <el-statistic :value="activeTask.fail_count || 0" title="失败">
                  <template #suffix>
                    <el-icon style="color: #F56C6C"><Close /></el-icon>
                  </template>
                </el-statistic>
              </el-col>
            </el-row>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="action-buttons">
          <template v-if="activeTask.status === 'running'">
            <el-button 
              type="warning" 
              :icon="VideoPause" 
              @click="handleTaskAction('pause', activeTask.id)">
              暂停
            </el-button>
          </template>
          
          <template v-if="activeTask.status === 'paused'">
            <el-button 
              type="primary" 
              :icon="CaretRight" 
              @click="handleTaskAction('resume', activeTask.id)">
              继续
            </el-button>
          </template>
          
          <template v-if="['running', 'paused'].includes(activeTask.status)">
            <el-button 
              type="danger" 
              :icon="CircleClose" 
              @click="handleTaskAction('stop', activeTask.id)">
              停止
            </el-button>
          </template>
          
          <template v-if="['completed', 'failed', 'stopped', 'ERROR'].includes(activeTask.status)">
            <el-button 
              type="danger" 
              :icon="Delete" 
              @click="handleTaskAction('delete', activeTask.id)">
              删除
            </el-button>
          </template>
        </div>
      </div>
      
      <div class="empty-state" v-else>
        <el-empty description="没有正在运行的任务" />
      </div>
      
      <div class="collapse-button" @click="drawerVisible = false">
        <el-icon><ArrowRight /></el-icon>
      </div>
    </el-drawer>
    
    <!-- 侧栏触发器 - 始终显示在页面右侧 -->
    <div class="drawer-trigger" @click="drawerVisible = true" v-if="!drawerVisible && activeTask">
      <div class="trigger-icon">
        <el-icon><ArrowLeft /></el-icon>
      </div>
      <div class="status-indicator" :class="getStatusClass(activeTask.status)"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { 
  CaretRight,
  VideoPause, 
  Check, 
  Close, 
  ArrowRight, 
  ArrowLeft,
  CircleClose,
  Delete
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { taskApi } from '../api'

const props = defineProps({
  task: {
    type: Object,
    default: null
  },
  surveyInfo: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['refresh', 'update:task', 'action', 'close'])

const drawerVisible = ref(false)
const activeTask = computed(() => props.task)
const refreshInterval = ref(null)
const refreshDelay = 3000 // 3秒刷新一次

// 启动刷新定时器
const startRefreshing = () => {
  if (refreshInterval.value) return
  
  refreshInterval.value = setInterval(async () => {
    if (!activeTask.value || !activeTask.value.id) return
    
    if (activeTask.value.status === 'running') {
      try {
        const response = await taskApi.refreshTask(activeTask.value.id)
        const updatedTask = response.data.data
        
        // 通知父组件更新任务数据
        emit('update:task', updatedTask)
        
        // 如果任务已完成或失败，停止刷新
        if (['completed', 'failed', 'stopped', 'ERROR'].includes(updatedTask.status)) {
          stopRefreshing()
        }
      } catch (error) {
        console.error('刷新任务状态失败:', error)
      }
    }
  }, refreshDelay)
}

// 停止刷新定时器
const stopRefreshing = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// 监听任务变化
watch(() => props.task, (newTask) => {
  if (newTask && newTask.id) {
    if (newTask.status === 'running') {
      drawerVisible.value = true
      startRefreshing()
    } else {
      stopRefreshing()
    }
  } else {
    stopRefreshing()
  }
}, { immediate: true })

// 监听抽屉可见性
watch(() => drawerVisible.value, (visible) => {
  if (!visible) {
    stopRefreshing()
  } else if (activeTask.value && activeTask.value.status === 'running') {
    startRefreshing()
  }
})

// 组件卸载时清理
onBeforeUnmount(() => {
  stopRefreshing()
})

// 计算任务进度
const calculateProgress = (task) => {
  // 如果有明确的progress字段，优先使用
  if (task.progress !== undefined && task.progress !== null) {
    // 确保进度在0-100之间
    return Math.min(Math.max(0, parseFloat(task.progress)), 100);
  }
  
  // 根据完成数量计算
  if (task.total_count > 0 && task.completed_count >= 0) {
    return Math.min(Math.round((task.completed_count / task.total_count) * 100), 100);
  }
  
  // 根据成功失败数量计算
  if (task.count > 0 && (task.success_count || task.error_count)) {
    const completedCount = (task.success_count || 0) + (task.error_count || 0);
    return Math.min(Math.round((completedCount / task.count) * 100), 100);
  }
  
  // 根据状态返回默认值
  if (task.status === 'completed') return 100;
  if (task.status === 'running') return 50;
  if (task.status === 'paused') return task.last_progress || 30;
  if (task.status === 'failed' || task.status === 'stopped' || task.status === 'ERROR') {
    return task.last_progress || 50;
  }
  
  return 0; // 默认为0
};

// 格式化进度显示
const formatProgress = (percentage) => {
  return activeTask.value?.status === 'completed' ? '完成' : 
         activeTask.value?.status === 'failed' ? '失败' : 
         `${percentage}%`
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    'pending': 'info',
    'running': 'primary',
    'paused': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return types[status] || 'info'
}

// 获取状态CSS类
const getStatusClass = (status) => {
  return `status-${status || 'default'}`
}

// 获取进度条状态
const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return ''
}

// 问卷标题
const surveyTitle = computed(() => {
  return props.surveyInfo?.title || '未知问卷'
})

// 格式化状态显示
const formatStatus = (status) => {
  const statusMap = {
    'pending': '等待中',
    'running': '运行中',
    'paused': '已暂停',
    'completed': '已完成',
    'failed': '已失败'
  }
  return statusMap[status] || status
}

// 格式化时间显示
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  
  try {
    const date = new Date(timeStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (e) {
    return timeStr
  }
}

// 处理任务操作
const handleTaskAction = (action, taskId) => {
  // 触发操作事件
  emit('action', action, taskId);
  
  // 如果是删除操作，关闭抽屉
  if (action === 'delete') {
    drawerVisible.value = false;
  }
};

// 处理抽屉关闭
const handleClose = (done) => {
  done()
  emit('close')
}

// 当任务变化时，自动打开抽屉
watch(() => props.task, (newTask) => {
  if (newTask && newTask.status === 'running') {
    drawerVisible.value = true
  }
}, { immediate: true })
</script>

<style scoped>
.task-status-drawer {
  position: relative;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.status-tag {
  font-size: 14px;
  padding: 6px 12px;
}

.task-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.progress-container {
  margin-bottom: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.progress-percentage {
  font-weight: bold;
}

.task-info {
  margin-bottom: 20px;
}

.task-id {
  font-family: monospace;
  background-color: var(--el-fill-color-light);
  padding: 2px 4px;
  border-radius: 3px;
  cursor: pointer;
}

.action-buttons {
  display: flex;
  justify-content: space-around;
  margin-top: 30px;
}

/* 抽屉触发器样式 */
.drawer-trigger {
  position: fixed;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  background: var(--el-color-primary-light-8);
  border-radius: 4px 0 0 4px;
  padding: 10px 5px;
  cursor: pointer;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid var(--el-border-color);
  border-right: none;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
}

.drawer-trigger:hover {
  background: var(--el-color-primary-light-7);
}

.trigger-icon {
  margin-bottom: 8px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: var(--el-color-info);
}

.status-running {
  background-color: var(--el-color-primary);
  animation: pulse 1.5s infinite;
}

.status-paused {
  background-color: var(--el-color-warning);
}

.status-completed {
  background-color: var(--el-color-success);
}

.status-failed {
  background-color: var(--el-color-danger);
}

.status-pending {
  background-color: var(--el-color-info);
}

/* 收起按钮 */
.collapse-button {
  position: absolute;
  top: 50%;
  left: -15px;
  transform: translateY(-50%);
  width: 28px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-color-primary-light-8);
  border-radius: 4px 0 0 4px;
  cursor: pointer;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.1);
}

.collapse-button:hover {
  background: var(--el-color-primary-light-7);
}

/* 脉冲动画 */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0);
  }
}

/* 暗色主题适配 */
:root[data-theme='dark'] .drawer-trigger {
  background-color: var(--el-bg-color-overlay);
}

:root[data-theme='dark'] .collapse-button {
  background-color: var(--el-bg-color-overlay);
}
</style>
