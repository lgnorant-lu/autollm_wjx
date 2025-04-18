<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <h2>欢迎使用问卷星自动化系统 <span class="version-tag">v{{ version }}</span></h2>
      <p>本系统可以帮助您自动填写问卷星问卷，提高问卷收集效率。</p>
    </el-card>

    <el-row :gutter="20" class="stat-row">
      <el-col :span="8">
        <el-card class="stat-card">
          <template #header>
            <div class="card-header">
              <span>问卷总数</span>
            </div>
          </template>
          <div class="stat-number">{{ stats.surveyCount }}</div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="stat-card">
          <template #header>
            <div class="card-header">
              <span>任务总数</span>
            </div>
          </template>
          <div class="stat-number">{{ stats.taskCount }}</div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="stat-card">
          <template #header>
            <div class="card-header">
              <span>成功提交数</span>
            </div>
          </template>
          <div class="stat-number">{{ stats.submitCount }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="recent-card">
      <template #header>
        <div class="card-header">
          <span>最近活动</span>
        </div>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="(activity, index) in recentActivities"
          :key="index"
          :timestamp="activity.time"
          :type="activity.type"
        >
          <span class="activity-content">{{ activity.content }}</span>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { surveyApi, taskApi } from '../api'

export default {
  name: 'HomeView',
  setup() {
    const stats = ref({
      surveyCount: 0,
      taskCount: 0,
      submitCount: 0
    })

    const recentActivities = ref([])

    async function fetchData() {
      try {
        // 获取统计信息
        const surveysResponse = await surveyApi.getAllSurveys()
        stats.value.surveyCount = surveysResponse.data?.data?.length || 0

        // 获取任务列表
        // 首先获取总数
        const countResponse = await taskApi.getTasks({ page: 1, page_size: 1 })
        const totalTasks = countResponse.data.total || 0
        stats.value.taskCount = totalTasks

        // 如果有任务，获取所有任务数据
        let allTasks = []
        if (totalTasks > 0) {
          const tasksResponse = await taskApi.getTasks({ page: 1, page_size: totalTasks })
          allTasks = tasksResponse.data.items || []
        }

        // 计算总成功提交数
        let submitCount = 0
        for (const task of allTasks) {
          if (task.success_count) {
            submitCount += task.success_count;
          }
        }
        stats.value.submitCount = submitCount

        // 生成最近活动
        recentActivities.value = generateRecentActivities(allTasks)
      } catch (error) {
        console.error('获取数据失败:', error)
      }
    }

    const generateRecentActivities = (tasks) => {
      const activities = []

      // 按创建时间排序，最新的在前面
      const sortedTasks = [...tasks].sort((a, b) => {
        return new Date(b.created_at) - new Date(a.created_at)
      })

      // 取最近5个任务
      const recentTasks = sortedTasks.slice(0, 5)

      for (const task of recentTasks) {
        let type = 'primary'
        if (task.status === 'completed') type = 'success'
        if (task.status === 'failed') type = 'danger'
        if (task.status === 'running') type = 'warning'

        activities.push({
          content: `任务 "${task.survey_title || '未知问卷'}" ${getStatusText(task.status)}`,
          time: task.created_at,
          type
        })
      }

      return activities
    }

    const getStatusText = (status) => {
      const statusMap = {
        'created': '已创建',
        'running': '正在运行',
        'paused': '已暂停',
        'completed': '已完成',
        'failed': '执行失败',
        'stopped': '已停止'
      }
      return statusMap[status] || status
    }

    // 获取版本信息
    const version = ref('')
    const fetchVersion = async () => {
      try {
        const response = await fetch('/api/config/version')
        const data = await response.json()
        version.value = data.version
      } catch (error) {
        console.error('Failed to fetch version:', error)
        version.value = '1.2.0' // 默认版本
      }
    }

    onMounted(() => {
      fetchData()
      fetchVersion()
    })

    return {
      stats,
      recentActivities,
      version
    }
  }
}
</script>

<style scoped>
.home-container {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.version-tag {
  font-size: 14px;
  color: #909399;
  background-color: #f0f2f5;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 10px;
  vertical-align: middle;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
}

.recent-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
