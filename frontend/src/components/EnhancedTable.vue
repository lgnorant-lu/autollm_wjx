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
        >
          <slot name="timeline" :item="item"></slot>
        </el-timeline-item>
      </el-timeline>
    </div>
    
    <!-- 高级分页 -->
    <div class="pagination-wrapper" v-show="props.showPagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
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
  }
})

const emit = defineEmits(['page-change', 'sort-change'])

const viewType = ref('table')
const currentPage = ref(1)
const pageSize = ref(10)

// 添加排序处理方法
const handleSortChange = (sort) => {
  emit('sort-change', sort)
}

const handleSizeChange = (val) => {
  pageSize.value = val
  emit('page-change', { page: currentPage.value, size: val })
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  emit('page-change', { page: val, size: pageSize.value })
}

const getTimelineType = (status) => {
  switch (status) {
    case 'completed': return 'success'
    case 'failed': return 'danger'
    case 'running': return 'primary'
    default: return 'info'
  }
}

// 在初始化时设置数据
const currentPageData = computed(() => {
  if (!props.showPagination) {
    return props.data || []
  }
  
  // 如果显示分页，则计算当前页数据
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return (props.data || []).slice(start, end)
})

// 重置分页当数据变化时
watch(() => props.data, () => {
  currentPage.value = 1
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