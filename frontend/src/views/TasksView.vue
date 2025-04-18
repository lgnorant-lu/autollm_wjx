<template>
  <div class="tasks-container">
    <h2>任务管理</h2>

    <!-- 任务创建表单 -->
    <TaskCreateForm @success="handleTaskCreated" />

    <!-- 任务状态侧栏 -->
    <TaskStatusDrawer
      :task="currentTask"
      :survey-info="selectedSurvey"
      @update:task="handleTaskUpdate"
      @action="handleTaskAction"
    />

    <!-- 任务仪表盘 -->
    <TaskDashboard
      v-if="currentTask && showDashboard"
      :task-data="currentTask"
    />

    <!-- 任务列表 -->
    <EnhancedTable
      :data="tasks"
      :loading="loading"
      :total="total || 0"
      row-key="id"
      :show-pagination="true"
      :initial-page="queryParams.page"
      :initial-page-size="queryParams.page_size"
      @page-change="handlePageChange"
      @size-change="handleSizeChange"
      @sort-change="handleSortChange"
    >
      <!-- 表格视图插槽 -->
      <template #default>
        <el-table-column prop="id" label="任务ID" width="180">
          <template #default="{ row }">
            <el-tooltip :content="row.id" placement="top">
              <span class="task-id">{{ truncateId(row.id) }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="survey_title" label="问卷标题" min-width="200">
          <template #default="{ row }">
            <el-tooltip :content="getSurveyTitle(row.survey_id)" placement="top">
              <span>{{ getSurveyTitle(row.survey_id) }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ formatStatus(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="200">
          <template #default="{ row }">
            <el-progress
              :percentage="calculateProgress(row)"
              :status="getProgressStatus(row.status)"
              :width="40"
              :stroke-width="5" />
          </template>
        </el-table-column>
        <el-table-column prop="count" label="总数" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button
                type="primary"
                size="small"
                @click="viewTaskDetails(row)"
                :icon="View"
              >
                详情
              </el-button>
              <el-button
                :type="row.status === 'running' ? 'warning' : 'success'"
                size="small"
                @click="toggleTaskStatus(row)"
                :disabled="['completed', 'failed', 'stopped'].includes(row.status)"
                :icon="row.status === 'running' ? VideoPause : CaretRight"
              >
                {{ row.status === 'running' ? '暂停' : '继续' }}
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="stopTask(row.id)"
                :icon="Delete"
              >
                停止
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="deleteTask(row.id)"
                :icon="Delete"
              >
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </template>

      <!-- 卡片视图插槽 -->
      <template #card="{ item }">
        <div class="task-card">
          <div class="task-card-header">
            <el-tag :type="getStatusType(item.status)" effect="dark">
              {{ formatStatus(item.status) }}
            </el-tag>
            <span class="task-id">{{ truncateId(item.id) }}</span>
          </div>

          <h3 class="task-title">{{ getSurveyTitle(item.survey_id) }}</h3>

          <div class="task-progress">
            <span>提交进度</span>
            <el-progress
              :percentage="calculateProgress(item)"
              :status="getProgressStatus(item.status)" />
          </div>

          <div class="task-stats">
            <div class="stat-item">
              <span class="stat-label">总提交</span>
              <span class="stat-value">{{ item.count }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">成功</span>
              <span class="stat-value">{{ item.success_count || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">失败</span>
              <span class="stat-value">{{ item.fail_count || 0 }}</span>
            </div>
          </div>

          <div class="task-footer">
            <span class="task-time">{{ item.created_at }}</span>
            <div class="task-actions">
              <el-button
                circle
                size="small"
                @click="viewTaskDetails(item)"
                :icon="View"
              />
              <el-button
                circle
                :type="item.status === 'running' ? 'warning' : 'success'"
                size="small"
                @click="toggleTaskStatus(item)"
                :disabled="['completed', 'failed', 'stopped'].includes(item.status)"
                :icon="item.status === 'running' ? VideoPause : CaretRight"
              />
              <el-button
                circle
                type="danger"
                size="small"
                @click="stopTask(item.id)"
                :icon="Delete"
              />
              <el-button
                circle
                type="danger"
                size="small"
                @click="deleteTask(item.id)"
                :icon="Delete"
              />
            </div>
          </div>
        </div>
      </template>

      <!-- 时间线视图插槽 -->
      <template #timeline="{ item }">
        <div class="task-timeline-item">
          <div class="timeline-header">
            <h4>{{ getSurveyTitle(item.survey_id) || '未知问卷' }}</h4>
            <el-tag :type="getStatusType(item.status)" size="small">
              {{ formatStatus(item.status) }}
            </el-tag>
          </div>

          <div class="task-progress">
            <el-progress
              :percentage="calculateProgress(item)"
              :status="getProgressStatus(item.status)"
              :stroke-width="6"
            />
          </div>

          <div class="timeline-stats">
            <span>提交: {{ item.count }}</span>
            <span>成功/失败: {{ item.success_count || 0 }}/{{ item.fail_count || 0 }}</span>
          </div>

          <div class="timeline-actions">
            <el-button
              type="primary"
              size="small"
              @click="viewTaskDetails(item)"
              :icon="View"
              text
            >
              详情
            </el-button>
            <el-button
              :type="item.status === 'running' ? 'warning' : 'success'"
              size="small"
              @click="toggleTaskStatus(item)"
              :disabled="['completed', 'failed', 'stopped'].includes(item.status)"
              :icon="item.status === 'running' ? VideoPause : CaretRight"
              text
            >
              {{ item.status === 'running' ? '暂停' : '继续' }}
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="stopTask(item.id)"
              :icon="Delete"
              text
            >
              停止
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteTask(item.id)"
              :icon="Delete"
              text
            >
              删除
            </el-button>
          </div>
        </div>
      </template>
    </EnhancedTable>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive, onBeforeUnmount } from 'vue';
import { Delete, View, CaretRight, VideoPause } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import TaskCreateForm from '@/components/TaskCreateForm.vue';
import TaskStatusDrawer from '@/components/TaskStatusDrawer.vue';
import TaskDashboard from '@/components/TaskDashboard.vue';
import EnhancedTable from '@/components/EnhancedTable.vue';
import { taskApi, surveyApi } from '@/api';

// 状态变量
const tasks = ref([]);
const loading = ref(false);
const total = ref(0);
const currentTask = ref(null);
const selectedSurvey = ref(null);
const surveyTitleCache = ref({});
const showDashboard = ref(false);

// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 10,
  sort_field: 'created_at',
  sort_order: 'desc'
});

// 轮询状态变量
const pollingInterval = ref(null);
const pollingTaskIds = ref([]);
const pollingDelay = 5000; // 5秒轮询一次

// 添加任务到轮询列表
const addTaskToPolling = (taskId) => {
  if (!pollingTaskIds.value.includes(taskId)) {
    pollingTaskIds.value.push(taskId);
    console.log(`添加任务到轮询列表: ${taskId}`);
  }

  // 如果轮询尚未开始，启动轮询
  if (!pollingInterval.value) {
    startPolling();
  }
};

// 从轮询列表移除任务
const removeTaskFromPolling = (taskId) => {
  const index = pollingTaskIds.value.indexOf(taskId);
  if (index !== -1) {
    pollingTaskIds.value.splice(index, 1);
    console.log(`从轮询列表移除任务: ${taskId}`);
  }

  // 如果没有任务需要轮询，停止轮询
  if (pollingTaskIds.value.length === 0) {
    stopPolling();
  }
};

// 启动轮询
const startPolling = () => {
  if (pollingInterval.value) return;

  console.log('启动任务状态轮询');
  pollingInterval.value = setInterval(async () => {
    for (const taskId of pollingTaskIds.value) {
      try {
        const response = await taskApi.refreshTask(taskId);
        const updatedTask = response.data.data;

        // 更新任务列表中的任务数据
        const index = tasks.value.findIndex(t => t.id === taskId);
        if (index !== -1) {
          // 保留原始引用，更新属性
          Object.assign(tasks.value[index], updatedTask);
          console.log(`更新任务状态: ${taskId}, 状态: ${updatedTask.status}, 进度: ${updatedTask.progress}%`);

          // 如果任务已完成、失败或停止，从轮询列表中移除
          if (['completed', 'failed', 'stopped', 'ERROR'].includes(updatedTask.status)) {
            removeTaskFromPolling(taskId);
          }
        }
      } catch (error) {
        console.error(`轮询任务状态失败: ${taskId}`, error);
      }
    }
  }, pollingDelay);
};

// 停止轮询
const stopPolling = () => {
  if (pollingInterval.value) {
    console.log('停止任务状态轮询');
    clearInterval(pollingInterval.value);
    pollingInterval.value = null;
  }
};

// 在组件销毁前停止轮询
onBeforeUnmount(() => {
  stopPolling();
});

// 获取任务列表
const fetchTasks = async () => {
  loading.value = true;
  try {
    const response = await taskApi.getTasks(queryParams);
    tasks.value = response.data.items.map(task => ({
      ...task,
      progress: task.progress !== undefined ? parseFloat(task.progress) : 0
    }));
    total.value = response.data.total;

    // 添加所有运行中的任务到轮询列表
    response.data.items.forEach(task => {
      if (task.status === 'running') {
        addTaskToPolling(task.id);
      }
    });
  } catch (error) {
    console.error('获取任务列表失败:', error);
    ElMessage.error('获取任务列表失败');
  } finally {
    loading.value = false;
  }
};

// 获取问卷信息
const fetchSurveys = async () => {
  try {
    const response = await surveyApi.getAllSurveys();
    const surveyMap = {};

    // 正确处理后端响应格式
    if (response.data && Array.isArray(response.data.data)) {
      response.data.data.forEach(survey => {
        surveyMap[survey.id] = survey.title || `问卷 ${survey.id}`;
      });
    } else if (response.data && Array.isArray(response.data)) {
      // 兼容直接返回数组的情况
      response.data.forEach(survey => {
        surveyMap[survey.id] = survey.title || `问卷 ${survey.id}`;
      });
    } else if (response.data && response.data.items && Array.isArray(response.data.items)) {
      // 兼容 {items: [...]} 格式
      response.data.items.forEach(survey => {
        surveyMap[survey.id] = survey.title || `问卷 ${survey.id}`;
      });
    }

    console.log('获取到问卷标题映射:', surveyMap);
    surveyTitleCache.value = surveyMap;
  } catch (error) {
    console.error('获取问卷列表失败:', error);
  }
};

// 获取问卷标题
const getSurveyTitle = (surveyId) => {
  return surveyTitleCache.value[surveyId] || `问卷 ${surveyId}`;
};

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

  // 根据状态返回默认值
  if (task.status === 'completed') return 100;
  if (task.status === 'running') return 50;
  if (task.status === 'paused') return task.last_progress || 30;
  if (task.status === 'failed' || task.status === 'stopped' || task.status === 'ERROR') {
    return task.last_progress || 50;
  }

  return 0; // 默认为0
};

// 任务状态相关函数
const getStatusType = (status) => {
  const statusMap = {
    'created': 'info',
    'running': 'primary',
    'paused': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'stopped': 'danger',
    'ERROR': 'exception'
  };
  return statusMap[status] || 'info';
};

const formatStatus = (status) => {
  const statusMap = {
    'created': '已创建',
    'running': '进行中',
    'paused': '已暂停',
    'completed': '已完成',
    'failed': '失败',
    'stopped': '已停止',
    'ERROR': '错误'
  };
  return statusMap[status] || status;
};

const getProgressStatus = (status) => {
  if (status === 'completed') return 'success';
  if (status === 'failed' || status === 'stopped' || status === 'ERROR') return 'exception';
  return status === 'running' ? '' : 'warning';
};

// 处理任务状态更新
const handleTaskUpdate = (updatedTask) => {
  if (!updatedTask || !updatedTask.id) return;

  // 更新当前选中的任务
  currentTask.value = updatedTask;

  // 同时更新列表中的任务
  const index = tasks.value.findIndex(t => t.id === updatedTask.id);
  if (index !== -1) {
    Object.assign(tasks.value[index], updatedTask);
  }

  console.log(`任务状态已更新: ${updatedTask.id}, 状态: ${updatedTask.status}, 进度: ${updatedTask.progress}%`);
};

// 处理任务操作
const handleTaskAction = async (action, taskId) => {
  if (!taskId) return;

  try {
    switch (action) {
      case 'view':
        const task = tasks.value.find(t => t.id === taskId);
        if (task) viewTaskDetails(task);
        break;
      case 'pause':
        await taskApi.pauseTask(taskId);
        removeTaskFromPolling(taskId);
        ElMessage.success('任务已暂停');
        break;
      case 'resume':
        await taskApi.resumeTask(taskId);
        addTaskToPolling(taskId);
        ElMessage.success('任务已恢复');
        break;
      case 'stop':
        await taskApi.stopTask(taskId);
        removeTaskFromPolling(taskId);
        ElMessage.success('任务已停止');
        break;
      case 'delete':
        await deleteTask(taskId);
        break;
    }

    // 刷新任务列表
    fetchTasks();
  } catch (error) {
    console.error(`执行任务操作失败: ${action}, ${taskId}`, error);
    ElMessage.error(`操作失败: ${error.message || '未知错误'}`);
  }
};

// 任务操作函数
const viewTaskDetails = (task) => {
  currentTask.value = task;
  fetchTaskSurveyInfo(task.survey_id);
  showDashboard.value = true;

  // 如果任务正在运行，添加到轮询列表
  if (task.status === 'running') {
    addTaskToPolling(task.id);
  }
};

const fetchTaskSurveyInfo = async (surveyId) => {
  try {
    const response = await surveyApi.getSurvey(surveyId);
    selectedSurvey.value = response.data;
  } catch (error) {
    console.error('获取问卷信息失败:', error);
    ElMessage.error('获取问卷详情失败');
  }
};

const toggleTaskStatus = async (task) => {
  try {
    if (task.status === 'running') {
      await taskApi.pauseTask(task.id);
      ElMessage.success('任务已暂停');
      // 从轮询列表移除
      removeTaskFromPolling(task.id);
    } else if (task.status === 'paused') {
      await taskApi.resumeTask(task.id);
      ElMessage.success('任务已恢复');
      // 添加到轮询列表
      addTaskToPolling(task.id);
    } else {
      ElMessage.warning('当前任务状态不支持此操作');
      return;
    }
    fetchTasks();
  } catch (error) {
    console.error('更改任务状态失败:', error);
    ElMessage.error('操作失败: ' + (error.response?.data?.message || error.message));
  }
};

const stopTask = async (taskId) => {
  try {
    await taskApi.stopTask(taskId);
    ElMessage.success('任务已停止');
    // 从轮询列表移除
    removeTaskFromPolling(taskId);
    fetchTasks();
  } catch (error) {
    console.error('停止任务失败:', error);
    const errorMessage = error.response?.data?.error || error.response?.data?.message || error.message || '未知错误';
    ElMessage.error('停止任务失败: ' + errorMessage);
  }
};

const deleteTask = async (taskId) => {
  try {
    await ElMessageBox.confirm('确定要删除此任务吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });

    await taskApi.deleteTask(taskId);
    ElMessage.success('任务删除成功');
    fetchTasks();

    // 如果删除的是当前选中的任务，清除选中状态
    if (currentTask.value && currentTask.value.id === taskId) {
      currentTask.value = null;
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error);
      ElMessage.error('删除任务失败');
    }
  }
};

// 辅助函数
const truncateId = (id) => {
  if (!id) return '';
  return id.length > 8 ? `${id.substring(0, 8)}...` : id;
};

// 分页和排序处理
const handlePageChange = (pageInfo) => {
  // 如果是对象，则提取page属性，否则直接使用参数值
  const page = typeof pageInfo === 'object' ? pageInfo.page : pageInfo;
  console.log('TasksView: 页码变化 ->', page, '原始参数:', pageInfo);
  queryParams.page = page;
  fetchTasks();
};

// 处理每页显示数量变化
const handleSizeChange = (size) => {
  console.log('TasksView: 页面大小变化 ->', size);
  queryParams.page_size = size;
  // 当页面大小变化时，重置到第一页
  queryParams.page = 1;
  fetchTasks();
};

const handleSortChange = ({ prop, order }) => {
  queryParams.sort_field = prop;
  queryParams.sort_order = order === 'descending' ? 'desc' : 'asc';
  fetchTasks();
};

// 任务创建成功回调
const handleTaskCreated = () => {
  ElMessage.success('任务创建成功');
  fetchTasks();
};

// 初始化
onMounted(() => {
  fetchTasks();
  fetchSurveys();
});
</script>

<style scoped>
.tasks-container {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* 卡片样式 */
.task-card {
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.task-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.task-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.task-id {
  font-family: monospace;
  color: var(--el-text-color-secondary);
}

.task-title {
  margin: 8px 0 16px;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-progress {
  margin: 16px 0;
}

.task-stats {
  display: flex;
  justify-content: space-around;
  margin: 16px 0;
  padding: 8px 0;
  border-top: 1px solid var(--el-border-color-lighter);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}

.task-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.task-actions {
  display: flex;
  gap: 8px;
}

/* 时间线样式 */
.task-timeline-item {
  padding: 16px;
  margin-bottom: 16px;
  border-left: 2px solid var(--el-color-primary);
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.timeline-header h4 {
  margin: 0;
  font-size: 16px;
}

.timeline-stats {
  display: flex;
  justify-content: space-between;
  margin: 12px 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.timeline-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}
</style>
