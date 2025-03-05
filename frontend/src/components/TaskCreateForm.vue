<template>
  <div class="task-create-form-container">
    <el-steps :active="activeStep" finish-status="success" simple>
      <el-step title="选择问卷" icon="Document" />
      <el-step title="配置选项" icon="Setting" />
      <el-step title="AI设置" icon="ChatDotRound" />
    </el-steps>
    
    <div class="step-content">
      <!-- 步骤1: 选择问卷 -->
      <div v-if="activeStep === 0" class="step-panel animate__animated animate__fadeIn">
        <el-card class="hover-card">
          <template #header>
            <div class="step-header">
              <el-icon><Document /></el-icon>
              <span>选择问卷</span>
            </div>
          </template>
          
          <el-form-item label="问卷" prop="survey_id">
            <el-select 
              v-model="form.survey_id" 
              placeholder="选择问卷" 
              style="width: 100%"
              @change="handleSurveyChange"
            >
              <el-option
                v-for="survey in surveys"
                :key="survey.id"
                :label="survey.title"
                :value="survey.id"
              />
            </el-select>
          </el-form-item>
          
          <div v-if="selectedSurvey" class="survey-preview">
            <h3>{{ selectedSurvey.title }}</h3>
            <p class="survey-detail"><el-icon><Link /></el-icon> {{ selectedSurvey.url }}</p>
            <p class="survey-detail"><el-icon><Timer /></el-icon> 添加时间: {{ selectedSurvey.created_at }}</p>
            <p class="survey-detail"><el-icon><Files /></el-icon> 题目数量: {{ selectedSurvey.question_count || '未知' }}</p>
          </div>
          
          <div class="step-actions">
            <el-button type="primary" @click="nextStep" :disabled="!form.survey_id">下一步</el-button>
          </div>
        </el-card>
      </div>
      
      <!-- 步骤2: 配置选项 -->
      <div v-else-if="activeStep === 1" class="step-panel animate__animated animate__fadeIn">
        <el-card class="hover-card">
          <template #header>
            <div class="step-header">
              <el-icon><Setting /></el-icon>
              <span>配置选项</span>
            </div>
          </template>
          
          <el-form-item label="提交次数" prop="count">
            <el-slider
              v-model="form.count"
              :min="1"
              :max="1000"
              :step="1"
              show-input
              show-stops
              :marks="{1: '1', 250: '250', 500: '500', 750: '750', 1000: '1000'}"
            />
          </el-form-item>
          
          <el-form-item label="使用代理">
            <el-switch v-model="form.use_proxy" />
          </el-form-item>
          
          <el-form-item label="代理URL" v-if="form.use_proxy" prop="proxy_url">
            <el-input 
              v-model="form.proxy_url" 
              placeholder="如: http://ip:port"
            />
          </el-form-item>
          
          <div class="step-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" @click="nextStep">下一步</el-button>
          </div>
        </el-card>
      </div>
      
      <!-- 步骤3: AI设置 -->
      <div v-else-if="activeStep === 2" class="step-panel animate__animated animate__fadeIn">
        <el-card class="hover-card">
          <template #header>
            <div class="step-header">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI设置</span>
            </div>
          </template>
          
          <el-form-item label="使用AI生成">
            <el-switch v-model="form.use_llm" />
          </el-form-item>
          
          <el-form-item v-if="form.use_llm" label="LLM模型">
            <el-radio-group v-model="form.llm_type" class="llm-options">
              <el-radio-button label="zhipu">
                <el-tooltip content="智谱GLM大语言模型" placement="top">
                  <div class="llm-option">
                    <img src="https://www.zhipuai.cn/favicon.ico" class="llm-icon" alt="智谱AI">
                    智谱GLM
                  </div>
                </el-tooltip>
              </el-radio-button>
              <el-radio-button label="baidu">
                <el-tooltip content="百度文心大语言模型" placement="top">
                  <div class="llm-option">
                    <img src="https://www.baidu.com/favicon.ico" class="llm-icon" alt="百度">
                    百度文心
                  </div>
                </el-tooltip>
              </el-radio-button>
              <el-radio-button label="aliyun">
                <el-tooltip content="阿里百炼大语言模型" placement="top">
                  <div class="llm-option">
                    <img src="https://www.aliyun.com/favicon.ico" class="llm-icon" alt="阿里云">
                    阿里百炼
                  </div>
                </el-tooltip>
              </el-radio-button>
              <el-radio-button label="openai">
                <el-tooltip content="OpenAI GPT模型" placement="top">
                  <div class="llm-option">
                    <img src="https://openai.com/favicon.ico" class="llm-icon" alt="OpenAI">
                    OpenAI
                  </div>
                </el-tooltip>
              </el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <div class="task-summary" v-if="form.survey_id">
            <h3>任务摘要</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="所选问卷">{{ getSurveyTitle() }}</el-descriptions-item>
              <el-descriptions-item label="提交次数">{{ form.count }}</el-descriptions-item>
              <el-descriptions-item label="使用代理">{{ form.use_proxy ? '是' : '否' }}</el-descriptions-item>
              <el-descriptions-item v-if="form.use_proxy" label="代理URL">{{ form.proxy_url }}</el-descriptions-item>
              <el-descriptions-item label="AI生成">{{ form.use_llm ? '是' : '否' }}</el-descriptions-item>
              <el-descriptions-item v-if="form.use_llm" label="LLM模型">{{ getLLMLabel() }}</el-descriptions-item>
            </el-descriptions>
          </div>
          
          <div class="step-actions">
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" @click="submit" :loading="loading">创建任务</el-button>
            <el-button @click="reset">重置</el-button>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 任务创建成功动画 -->
    <el-dialog v-model="showSuccessDialog" width="30%" center append-to-body class="success-dialog">
      <div class="success-animation">
        <div class="checkmark-circle">
          <div class="checkmark draw"></div>
        </div>
        <h2>任务创建成功!</h2>
        <p>您的任务已成功创建并开始运行</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { surveyApi, taskApi } from '../api'
import { Document, Setting, ChatDotRound, Link, Timer, Files } from '@element-plus/icons-vue'

const emit = defineEmits(['success'])

const loading = ref(false)
const surveys = ref([])
const formRef = ref(null)
const activeStep = ref(0)
const selectedSurvey = ref(null)
const showSuccessDialog = ref(false)

// 表单数据
const form = reactive({
  survey_id: '',
  count: 10,
  use_proxy: false,
  proxy_url: '',
  use_llm: false,
  llm_type: 'aliyun' // 默认使用阿里云
})

// 表单验证规则
const rules = {
  survey_id: [{ required: true, message: '请选择问卷', trigger: 'change' }],
  count: [{ required: true, message: '请输入提交次数', trigger: 'blur' }],
  proxy_url: [
    { 
      validator: (rule, value, callback) => {
        if (form.use_proxy && !value) {
          callback(new Error('请输入代理URL'))
        } else if (form.use_proxy && value && !validateProxyUrl(value)) {
          callback(new Error('代理URL格式不正确'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 验证代理URL格式
const validateProxyUrl = (url) => {
  if (!url) return true
  return /^(http|https):\/\/[a-zA-Z0-9]+([\-\.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,}(:[0-9]{1,5})?(\/.*)?$/.test(url)
}

// 获取问卷列表
const fetchSurveys = async () => {
  try {
    const response = await surveyApi.getAllSurveys()
    surveys.value = response.data.data || []
  } catch (error) {
    console.error('获取问卷列表失败:', error)
    ElMessage.error('获取问卷列表失败')
  }
}

// 步骤导航
const nextStep = () => {
  if (activeStep.value < 2) {
    activeStep.value++
  }
}

const prevStep = () => {
  if (activeStep.value > 0) {
    activeStep.value--
  }
}

// 处理问卷选择变更
const handleSurveyChange = (surveyId) => {
  const survey = surveys.value.find(s => s.id === surveyId)
  if (survey) {
    selectedSurvey.value = survey
  }
}

// 获取问卷标题
const getSurveyTitle = () => {
  const survey = surveys.value.find(s => s.id === form.survey_id)
  return survey ? survey.title : '未选择'
}

// 获取LLM模型名称
const getLLMLabel = () => {
  const llmTypes = {
    zhipu: '智谱GLM',
    baidu: '百度文心',
    aliyun: '阿里百炼',
    openai: 'OpenAI'
  }
  return llmTypes[form.llm_type] || form.llm_type
}

// 提交表单
const submit = async () => {
  loading.value = true
  try {
    // 构建表单数据
    const formData = {
      survey_id: form.survey_id,
      count: parseInt(form.count),
      use_proxy: form.use_proxy,
      proxy_url: form.use_proxy ? form.proxy_url : '',
      use_llm: form.use_llm,
      llm_type: form.use_llm ? form.llm_type : ''
    }
    
    // 调试输出
    console.log('提交表单数据:', formData)
    
    const result = await taskApi.createTask(formData)
    
    // 显示成功动画
    showSuccessDialog.value = true
    setTimeout(() => {
      showSuccessDialog.value = false
      // 通知父组件
      emit('success', result.data)
      // 重置表单和步骤
      reset()
    }, 2000)
    
  } catch (error) {
    console.error('创建任务失败:', error)
    ElMessage.error('创建任务失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

// 重置表单
const reset = () => {
  form.survey_id = ''
  form.count = 10
  form.use_proxy = false
  form.proxy_url = ''
  form.use_llm = false
  form.llm_type = 'aliyun'
  activeStep.value = 0
  selectedSurvey.value = null
}

onMounted(() => {
  fetchSurveys()
})
</script>

<style>
@import 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css';

.task-create-form-container {
  margin: 20px 0;
}

.step-content {
  margin-top: 30px;
}

.step-panel {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
  color: var(--el-color-primary);
}

.step-actions {
  margin-top: 30px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.survey-preview {
  margin-top: 20px;
  padding: 15px;
  background: var(--secondary-bg);
  border-radius: 8px;
  transition: all 0.3s;
}

.survey-detail {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  color: var(--el-text-color-secondary);
}

.llm-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.llm-option {
  display: flex;
  align-items: center;
  gap: 5px;
}

.llm-icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
}

.task-summary {
  margin-top: 25px;
  padding: 20px;
  background: var(--secondary-bg);
  border-radius: 8px;
}

/* 成功动画 */
.success-dialog .el-dialog__body {
  padding: 30px;
}

.success-animation {
  text-align: center;
  padding: 20px;
}

.checkmark-circle {
  width: 80px;
  height: 80px;
  position: relative;
  display: inline-block;
  vertical-align: top;
  margin-bottom: 20px;
}

.checkmark-circle .background {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--el-color-success);
  position: absolute;
}

.checkmark-circle .checkmark {
  border-radius: 5px;
}

.checkmark-circle .checkmark.draw:after {
  animation-delay: 100ms;
  animation-duration: 1s;
  animation-timing-function: ease;
  animation-name: checkmark;
  transform: scaleX(-1) rotate(135deg);
  animation-fill-mode: forwards;
}

.checkmark-circle .checkmark:after {
  opacity: 0;
  height: 40px;
  width: 20px;
  transform-origin: left top;
  border-right: 8px solid var(--el-color-success);
  border-top: 8px solid var(--el-color-success);
  content: '';
  left: 25px;
  top: 45px;
  position: absolute;
}

@keyframes checkmark {
  0% {
    height: 0;
    width: 0;
    opacity: 1;
  }
  20% {
    height: 0;
    width: 20px;
    opacity: 1;
  }
  40% {
    height: 40px;
    width: 20px;
    opacity: 1;
  }
  100% {
    height: 40px;
    width: 20px;
    opacity: 1;
  }
}
</style>