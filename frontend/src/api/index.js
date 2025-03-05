import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

// 创建Axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 问卷相关API
export const surveyApi = {
  // 解析问卷
  parseSurvey(url) {
    return apiClient.post('/surveys/parse', { url })
  },
  
  // 获取所有问卷
  getAllSurveys() {
    return apiClient.get('/surveys')
  },
  
  // 获取问卷详情
  getSurvey(id) {
    return apiClient.get(`/surveys/${id}`)
  },
  
  // 删除问卷
  deleteSurvey(id) {
    return apiClient.delete(`/surveys/${id}`)
  }
}

// 任务相关API
export const taskApi = {
  // 创建任务
  createTask: async (taskData) => {
    console.log('创建任务数据:', taskData); // 添加日志

    // 确保数据格式正确
    const payload = {
      survey_id: taskData.survey_id,
      count: parseInt(taskData.count, 10),
      use_proxy: !!taskData.use_proxy,
      proxy_url: taskData.proxy_url || '',
      use_llm: !!taskData.use_llm,
      llm_type: taskData.llm_type || 'aliyun'  // 确保有默认值
    };

    try {
      const response = await apiClient.post('/tasks', payload);
      return response.data;
    } catch (error) {
      console.error('创建任务失败:', error);
      throw error;
    }
  },
  
  // 获取任务列表，支持分页和排序
  getTasks(params = {}) {
    return apiClient.get('/tasks', { params })
  },
  
  // 获取任务详情
  getTask(id) {
    return apiClient.get(`/tasks/${id}`)
  },
  
  // 刷新任务状态
  refreshTask(id) {
    return apiClient.post(`/tasks/${id}/refresh`)
  },
  
  // 更新任务状态
  updateTaskStatus(id, status) {
    return apiClient.put(`/tasks/${id}/status`, { status })
  },
  
  // 暂停任务
  pauseTask(id) {
    return apiClient.post(`/tasks/${id}/pause`)
  },
  
  // 恢复任务
  resumeTask(id) {
    return apiClient.post(`/tasks/${id}/resume`)
  },
  
  // 停止任务
  stopTask(id) {
    return apiClient.post(`/tasks/${id}/stop`)
  },
  
  // 删除任务
  deleteTask(id) {
    return apiClient.delete(`/tasks/${id}`)
  }
}

// 配置相关API
export const configApi = {
  // 获取系统配置
  getConfig() {
    return apiClient.get('/config')
  },
  
  // 更新系统配置
  updateConfig(configData) {
    return apiClient.put('/config', configData)
  }
}