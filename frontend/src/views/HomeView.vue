<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <h2>欢迎使用问卷星自动化系统</h2>
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
          {{ activity.content }}
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
        const tasksResponse = await taskApi.getTasks()
        const tasks = tasksResponse.data.items || []
        stats.value.taskCount = tasks.length
        
        // 计算总成功提交数
        let submitCount = 0
        for (const task of tasks) {
          if (task.success_count) {
            submitCount += task.success_count;
          }
        }
        stats.value.submitCount = submitCount
        
        // 生成最近活动
        recentActivities.value = generateRecentActivities(tasks)
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
          content: `任务 "${task.survey_title}" ${getStatusText(task.status)}`,
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
    
    onMounted(() => {
      fetchData()
    })
    
    return {
      stats,
      recentActivities
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
