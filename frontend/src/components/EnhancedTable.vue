<template>
  <div class="enhanced-table">
    <!-- 视图切换 -->
    <div class="view-switch">
      <el-radio-group v-model="viewType">
        <el-radio-button value="table">表格视图</el-radio-button>
        <el-radio-button value="card">卡片视图</el-radio-button>
        <el-radio-button value="timeline">时间线视图</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 表格视图 -->
    <div v-if="viewType === 'table'" class="table-view">
      <el-table
        :data="currentPageData"
        v-loading="loading"
        @sort-change="handleSortChange"
        row-key="id"
      >
        <slot></slot>
      </el-table>
    </div>

    <!-- 卡片视图 -->
    <div v-else-if="viewType === 'card'" class="card-view">
      <el-row :gutter="20">
        <el-col
          v-for="item in currentPageData"
          :key="item.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card
            class="data-card"
            :body-style="{ padding: '0px' }"
          >
            <slot name="card" :item="item"></slot>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 时间线视图 -->
    <div v-else class="timeline-view">
      <el-timeline>
        <el-timeline-item
          v-for="item in currentPageData"
          :key="item.id"
          :timestamp="item.created_at"
          :type="getTimelineType(item.status)"
          :color="getTimelineColor(item.status)"
        >
          <slot name="timeline" :item="item"></slot>
        </el-timeline-item>
      </el-timeline>
    </div>

    <!-- 高级分页 -->
    <div class="pagination-wrapper" v-show="props.showPagination">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="props.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      >
      </el-pagination>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  total: {
    type: Number,
    required: true,
    default: 0
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  initialPage: {
    type: Number,
    default: 1
  },
  initialPageSize: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits(['page-change', 'size-change', 'sort-change'])

const viewType = ref('table')
const currentPage = ref(props.initialPage)
const pageSize = ref(props.initialPageSize)

// 添加排序处理方法
const handleSortChange = (sort) => {
  emit('sort-change', sort)
}

const handleSizeChange = (val) => {
  // 更新页面大小
  pageSize.value = val
  // 发送页面大小变化事件
  emit('size-change', val)
  // 重置到第一页
  currentPage.value = 1
  // 发送页码变化事件
  emit('page-change', 1)
  // 打印日志，便于调试
  console.log('EnhancedTable: 页面大小变化 ->', val)
}

const handleCurrentChange = (val) => {
  // 更新当前页码
  currentPage.value = val
  // 只发送页码，不发送对象
  emit('page-change', val)
  // 打印日志，便于调试
  console.log('EnhancedTable: 页码变化 ->', val)
}

const getTimelineType = (status) => {
  switch (status) {
    case 'completed': return 'success'
    case 'failed': return 'danger'
    case 'running': return 'primary'
    default: return 'info'
  }
}

const getTimelineColor = (status) => {
  switch (status) {
    case 'completed': return '#67C23A' // 成功绿色
    case 'failed': return '#F56C6C' // 失败红色
    case 'running': return '#409EFF' // 运行蓝色
    case 'paused': return '#E6A23C' // 暂停黄色
    default: return '#909399' // 默认灰色
  }
}

// 直接使用传入的数据，不在前端进行分页
const currentPageData = computed(() => {
  return props.data || []
})

// 监听数据变化
watch(() => props.data, (newData, oldData) => {
  // 只有当数据长度变化时才重置分页
  if (!oldData || newData.length !== oldData.length) {
    currentPage.value = 1
  }
})
</script>

<style scoped>
.enhanced-table {
  --card-transition: all 0.3s ease;
}

.view-switch {
  margin-bottom: 20px;
}

.data-card {
  margin-bottom: 20px;
  transition: var(--card-transition);
  cursor: pointer;
}

.data-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.timeline-view {
  padding: 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.pagination-info {
  margin-left: 15px;
  color: var(--el-text-color-secondary);
}

/* 暗色主题适配 */
:root[data-theme='dark'] .data-card {
  background: var(--el-bg-color-overlay);
}
</style>