<template>
  <div class="surveys-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>问卷管理</h2>
          <el-button type="primary" @click="showAddDialog">添加问卷</el-button>
        </div>
      </template>
      
      <el-table v-loading="loading" :data="surveys" style="width: 100%">
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="url" label="URL" show-overflow-tooltip />
        <el-table-column prop="created_at" label="添加时间" width="180" />
        <el-table-column label="操作" width="250">
          <template #default="scope">
            <el-button size="small" @click="viewSurvey(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="createTask(scope.row)">创建任务</el-button>
            <el-button size="small" type="danger" @click="confirmDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加问卷对话框 -->
    <el-dialog v-model="addDialogVisible" title="添加问卷" width="500px">
      <el-form :model="surveyForm" label-width="80px">
        <el-form-item label="问卷URL">
          <el-input v-model="surveyForm.url" placeholder="输入问卷星URL，如 https://www.wjx.cn/vm/xxxx.aspx" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addSurvey" :loading="addLoading">解析并添加</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 查看问卷对话框 -->
    <el-dialog v-model="viewDialogVisible" title="问卷详情" width="800px">
      <div v-if="currentSurvey">
        <h3>{{ currentSurvey.title }}</h3>
        <p><strong>URL: </strong>{{ currentSurvey.url }}</p>
        <p><strong>问卷ID: </strong>{{ currentSurvey.id }}</p>
        <p><strong>创建时间: </strong>{{ currentSurvey.created_at }}</p>
        
        <el-divider />
        
        <h3>题目列表</h3>
        <el-collapse v-if="currentSurvey.questions && currentSurvey.questions.length">
          <el-collapse-item v-for="question in currentSurvey.questions" :key="question.index" 
                           :title="`${question.index}. ${question.title} (${getQuestionType(question.type)})`">
            <div v-if="question.options && question.options.length">
              <p><strong>选项:</strong></p>
              <el-tag v-for="(option, idx) in question.options" :key="idx" 
                     style="margin-right: 5px; margin-bottom: 5px;">
                {{ option }}
              </el-tag>
            </div>
          </el-collapse-item>
        </el-collapse>
        <el-empty v-else description="没有题目数据"></el-empty>
      </div>
    </el-dialog>
    
    <!-- 创建任务对话框 -->
    <el-dialog v-model="taskDialogVisible" title="创建任务" width="500px">
      <el-form :model="taskForm" label-width="120px">
        <el-form-item label="问卷">
          <el-input v-model="taskForm.surveyTitle" disabled />
        </el-form-item>
        
        <el-form-item label="填写数量">
          <el-input-number v-model="taskForm.count" :min="1" :max="1000" />
        </el-form-item>
        
        <el-form-item label="使用代理">
          <el-switch v-model="taskForm.useProxy" />
        </el-form-item>
        
        <el-form-item label="代理URL" v-if="taskForm.useProxy">
          <el-input v-model="taskForm.proxyUrl" placeholder="输入代理服务URL" />
        </el-form-item>
        
        <el-form-item label="使用AI生成答案">
          <el-switch v-model="taskForm.useLLM" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="taskDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTask" :loading="taskLoading">创建任务</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { surveyApi, taskApi } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'SurveysView',
  
  setup() {
    const loading = ref(false)
    const addLoading = ref(false)
    const taskLoading = ref(false)
    
    const surveys = ref([])
    const currentSurvey = ref(null)
    
    const addDialogVisible = ref(false)
    const viewDialogVisible = ref(false)
    const taskDialogVisible = ref(false)
    
    const surveyForm = ref({
      url: ''
    })
    
    const taskForm = ref({
      surveyId: '',
      surveyTitle: '',
      count: 10,
      useProxy: false,
      proxyUrl: '',
      useLLM: false
    })
    
    // 获取所有问卷
    const fetchSurveys = async () => {
      loading.value = true
      try {
        const response = await surveyApi.getAllSurveys()
        console.log('获取问卷响应:', response);
        
        // 兼容不同的响应格式
        if (Array.isArray(response.data)) {
          surveys.value = response.data
        } else if (response.data && Array.isArray(response.data.data)) {
          surveys.value = response.data.data
        } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
          surveys.value = response.data.data
        } else {
          surveys.value = []
          console.log('没有找到问卷数据，使用空数组');
        }
      } catch (error) {
        console.error('获取问卷列表失败:', error)
        ElMessage.error('获取问卷列表失败: ' + (error.response?.data?.error || error.message || '未知错误'))
        surveys.value = []
      } finally {
        loading.value = false
      }
    }
    
    // 显示添加对话框
    const showAddDialog = () => {
      surveyForm.value.url = ''
      addDialogVisible.value = true
    }
    
    // 添加问卷
    const addSurvey = async () => {
      if (!surveyForm.value.url) {
        ElMessage.warning('请输入问卷URL')
        return
      }
      
      addLoading.value = true
      try {
        const response = await surveyApi.parseSurvey(surveyForm.value.url)
        ElMessage.success('问卷解析成功')
        addDialogVisible.value = false
        fetchSurveys()
      } catch (error) {
        console.error('解析问卷失败:', error)
        ElMessage.error('解析问卷失败: ' + (error.response?.data?.error || '未知错误'))
      } finally {
        addLoading.value = false
      }
    }
    
    // 查看问卷详情
    const viewSurvey = async (survey) => {
      try {
        const response = await surveyApi.getSurvey(survey.id)
        currentSurvey.value = response.data.data || {}
        viewDialogVisible.value = true
      } catch (error) {
        console.error('获取问卷详情失败:', error)
        ElMessage.error('获取问卷详情失败')
      }
    }
    
    // 准备创建任务
    const createTask = (survey) => {
      taskForm.value.surveyId = survey.id
      taskForm.value.surveyTitle = survey.title
      taskDialogVisible.value = true
    }
    
    // 提交任务
    const submitTask = async () => {
      taskLoading.value = true
      try {
        const taskData = {
          survey_id: taskForm.value.surveyId,
          count: taskForm.value.count,
          use_proxy: taskForm.value.useProxy,
          proxy_url: taskForm.value.proxyUrl,
          use_llm: taskForm.value.useLLM
        }
        
        const response = await taskApi.createTask(taskData)
        ElMessage.success('任务创建成功')
        taskDialogVisible.value = false
      } catch (error) {
        console.error('创建任务失败:', error)
        ElMessage.error('创建任务失败: ' + (error.response?.data?.error || '未知错误'))
      } finally {
        taskLoading.value = false
      }
    }
    
    // 确认删除
    const confirmDelete = (survey) => {
      ElMessageBox.confirm(
        `确定要删除问卷 "${survey.title}" 吗?`,
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
        .then(async () => {
          try {
            await surveyApi.deleteSurvey(survey.id)
            ElMessage.success('删除成功')
            fetchSurveys()
          } catch (error) {
            console.error('删除问卷失败:', error)
            ElMessage.error('删除失败')
          }
        })
        .catch(() => {
          // 用户取消操作
        })
    }
    
    // 获取题型名称
    const getQuestionType = (type) => {
      const typeMap = {
        1: '填空题',
        2: '矩阵题',
        3: '单选题',
        4: '多选题',
        5: '评分题',
        6: '排序题',
        7: '量表题'
      }
      return typeMap[type] || `未知类型(${type})`
    }
    
    onMounted(() => {
      fetchSurveys()
    })
    
    return {
      loading,
      addLoading,
      taskLoading,
      surveys,
      currentSurvey,
      addDialogVisible,
      viewDialogVisible,
      taskDialogVisible,
      surveyForm,
      taskForm,
      showAddDialog,
      addSurvey,
      viewSurvey,
      createTask,
      submitTask,
      confirmDelete,
      getQuestionType
    }
  }
}
</script>

<style scoped>
.surveys-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>