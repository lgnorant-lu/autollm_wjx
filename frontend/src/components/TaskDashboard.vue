<template>
  <div class="task-dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              当前任务进度
            </div>
          </template>
          <el-progress 
            type="circle" 
            :percentage="taskProgress"
            :status="taskStatus"
          />
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-s-claim"></i>
              提交统计
            </div>
          </template>
          <div class="stat-grid">
            <div class="stat-item">
              <div class="stat-value success">{{ successCount }}</div>
              <div class="stat-label">成功</div>
            </div>
            <div class="stat-item">
              <div class="stat-value error">{{ failCount }}</div>
              <div class="stat-label">失败</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-time"></i>
              提交时间分布
            </div>
          </template>
          <div class="chart-container">
            <!-- 使用echarts绘制提交时间分布图 -->
            <v-chart :option="chartOption" autoresize />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { TrendCharts, Timer, Document } from '@element-plus/icons-vue'

const props = defineProps({
  taskData: {
    type: Object,
    required: true
  }
})

// 计算任务进度
const taskProgress = computed(() => {
  if (!props.taskData) return 0
  
  // 确保进度值在0-100之间
  const rawProgress = Math.round((props.taskData.progress || 0) * 100)
  return Math.min(100, Math.max(0, rawProgress))
})

// 计算任务状态
const taskStatus = computed(() => {
  if (!props.taskData) return ''
  const status = props.taskData.status
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  if (status === 'running') return ''
  return 'warning'
})

// 统计数据
const successCount = computed(() => props.taskData?.success_count || 0)
const failCount = computed(() => props.taskData?.fail_count || 0)

// 图表配置
const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['提交次数']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: props.taskData?.time_distribution?.map(item => item.time) || []
  },
  yAxis: {
    type: 'value'
  },
  series: [{
    name: '提交次数',
    type: 'line',
    data: props.taskData?.time_distribution?.map(item => item.count) || [],
    areaStyle: {}
  }]
}))
</script>

<style scoped>
.task-dashboard {
  margin-top: 20px;
}

.data-card {
  transition: all 0.3s;
}

.data-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.stat-value.success { color: #67C23A; }
.stat-value.error { color: #F56C6C; }

.chart-container {
  height: 300px;
}
</style> 