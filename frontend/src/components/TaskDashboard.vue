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
            <v-chart :option="chartOption" autoresize style="height: 300px;" />
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
const chartOption = computed(() => {
  // 检查是否有时间分布数据
  const hasData = props.taskData?.time_distribution && props.taskData.time_distribution.length > 0

  // 获取实际数据或生成模拟数据
  let timeData = []
  let countData = []

  if (hasData) {
    // 过滤掉count为0的数据点，除非只有一个数据点
    const filteredData = props.taskData.time_distribution.length > 1
      ? props.taskData.time_distribution.filter(item => item.count > 0)
      : props.taskData.time_distribution

    // 如果过滤后没有数据，使用原始数据
    const dataToUse = filteredData.length > 0 ? filteredData : props.taskData.time_distribution

    // 如果数据点过多，可以进行采样，每隔几个点取一个
    let finalData = dataToUse
    if (dataToUse.length > 20) {
      // 如果数据点超过20个，进行采样
      const step = Math.ceil(dataToUse.length / 20)
      finalData = dataToUse.filter((_, index) => index % step === 0)

      // 确保包含最后一个数据点
      if (finalData[finalData.length - 1] !== dataToUse[dataToUse.length - 1]) {
        finalData.push(dataToUse[dataToUse.length - 1])
      }
    }

    timeData = finalData.map(item => item.time)
    countData = finalData.map(item => item.count)
  } else {
    // 模拟数据
    timeData = [props.taskData?.create_time || '00:00:00']
    countData = [0]
  }

  // 计算Y轴最大值，确保至少为1
  const maxCount = Math.max(...countData, 1)

  return {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>{a}: {c}'
    },
    legend: {
      data: ['提交次数'],
      textStyle: {
        color: '#333'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true
    },
    toolbox: {
      show: true,
      orient: 'horizontal',
      itemSize: 15,
      itemGap: 10,
      right: '5%',
      top: '0%',
      showTitle: true,
      feature: {
        dataZoom: {
          show: true,
          title: {
            zoom: '区域缩放',
            back: '还原缩放'
          },
          icon: {
            zoom: 'path://M0,13.5h26.9 M13.5,26.9V0 M32.1,13.5H58V58H13.5 V32.1',
            back: 'path://M22,1.4C12,1.4,3.8,9.6,3.8,19.6c0,10,8.2,18.2,18.2,18.2c10,0,18.2-8.2,18.2-18.2C40.2,9.6,32,1.4,22,1.4z M22,31.5c-6.5,0-11.9-5.3-11.9-11.9c0-6.5,5.3-11.9,11.9-11.9c6.5,0,11.9,5.3,11.9,11.9C33.9,26.2,28.5,31.5,22,31.5z M18.1,21.4h7.9v-3.5h-7.9V21.4z'
          },
          xAxisIndex: 'all',  // 只缩放X轴
          yAxisIndex: false   // 不缩放Y轴
        },
        restore: {
          show: true,
          title: '还原',
          icon: 'path://M3.8,33.4 M47,18.9h9.8V8.7 M56.8,8.7C41.3,3.8,21.7,3.8,8.7,8.7C5.6,9.7,3.8,11.5,3.8,14.2c0,2.6,2.1,5.2,5.2,6.3 M10.6,33.4h9.8V43.5 M20.4,43.5C35.8,48.1,54.7,47.9,68.2,43.3c2.9-1.2,5.2-2.6,5.2-5.2c0-2.6-2.1-5.2-5.2-6.3'
        },
        saveAsImage: {
          show: true,
          title: '保存为图片',
          icon: 'path://M4.7,22.9L29.3,45.5L54.7,23.4M4.6,43.6L4.6,58L53.8,58L53.8,43.6M29.2,45.1L29.2,0'
        }
      }
    },
    dataZoom: [{
      type: 'inside',
      start: 0,
      end: 100,
      minValueSpan: 1,  // 最小缩放范围
      maxValueSpan: timeData.length,  // 最大缩放范围
      xAxisIndex: [0],  // 只缩放X轴，不缩放Y轴
      zoomLock: false,  // 不锁定缩放比例
      filterMode: 'filter'  // 数据过滤模式
    }],
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: timeData,
      axisLine: {
        lineStyle: {
          color: '#ddd',
          width: 1
        }
      },
      axisTick: {
        show: false  // 隐藏刻度线
      },
      splitLine: {
        show: false  // 隐藏网格线
      },
      axisLabel: {
        rotate: 45,
        margin: 8,
        color: '#666',
        fontSize: 12,
        formatter: function(value) {
          // 如果是包含秒的时间格式，只显示小时和分钟
          if (value.length === 8) { // HH:MM:SS格式
            return value.substring(0, 5); // 只显示HH:MM
          }
          return value;
        },
        interval: 'auto',  // 自动计算间隔，避免标签重叠
        showMaxLabel: true,  // 确保显示最后一个标签
        showMinLabel: true   // 确保显示第一个标签
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,  // 确保显示整数刻度
      max: maxCount + 1,  // 设置最大值比实际数据多1
      axisLine: {
        show: false  // 隐藏Y轴线
      },
      axisTick: {
        show: false  // 隐藏刻度线
      },
      splitLine: {
        lineStyle: {
          color: '#eee',
          type: 'dashed'
        }
      },
      axisLabel: {
        color: '#666',
        fontSize: 12
      }
    },
    series: [{
      name: '提交次数',
      type: 'line',
      data: countData,
      showSymbol: true,  // 显示数据点
      symbolSize: 8,     // 数据点大小
      hoverAnimation: true,  // 鼠标悬停时数据点动画
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: 'rgba(80, 141, 255, 0.8)'
          }, {
            offset: 1,
            color: 'rgba(80, 141, 255, 0.1)'
          }]
        },
        opacity: 0.8,
        shadowColor: 'rgba(0, 0, 0, 0.1)',
        shadowBlur: 10
      },
      lineStyle: {
        width: 3,
        type: 'solid',
        color: '#409EFF',
        shadowColor: 'rgba(0, 0, 0, 0.3)',
        shadowBlur: 2,
        shadowOffsetY: 2
      },
      itemStyle: {
        color: '#409EFF',
        borderColor: '#fff',
        borderWidth: 2,
        shadowColor: 'rgba(0, 0, 0, 0.5)',
        shadowBlur: 5
      },
      emphasis: {
        scale: true,
        itemStyle: {
          color: '#409EFF',
          borderColor: '#fff',
          borderWidth: 3,
          shadowBlur: 10,
          shadowColor: 'rgba(64, 158, 255, 0.5)'
        },
        lineStyle: {
          width: 4
        }
      },
      smooth: 0.3  // 设置平滑系数，0-1之间
    }]
  }
})
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
  height: 350px;
  margin-top: 10px;
  position: relative;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.05);
}
</style>