<template>
  <div class="settings-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>系统设置</h2>
        </div>
      </template>
      
      <el-form :model="configForm" label-width="120px" v-loading="loading">
        <h3>代理设置</h3>
        <el-form-item label="启用代理">
          <el-switch v-model="configForm.proxy_settings.enabled" />
        </el-form-item>
        
        <el-form-item label="代理URL" v-if="configForm.proxy_settings.enabled">
          <el-input 
            v-model="configForm.proxy_settings.url" 
            placeholder="输入代理服务URL，如 http://ip:port 或 API地址"
          />
          <span class="form-tip">此URL将用于所有未指定代理的任务</span>
        </el-form-item>
        
        <el-divider />
        
        <h3>AI答案生成设置</h3>
        <el-form-item label="启用AI生成">
          <el-switch v-model="configForm.llm_settings.enabled" />
        </el-form-item>
        
        <template v-if="configForm.llm_settings.enabled">
          <el-form-item label="AI服务商">
            <el-select v-model="configForm.llm_settings.provider">
              <el-option label="智谱AI" value="zhipu" />
              <el-option label="百度文心" value="baidu" />
              <el-option label="OpenAI" value="openai" />
              <el-option label="阿里百炼" value="aliyun" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="API密钥">
            <el-input 
              v-model="configForm.llm_settings.api_key" 
              placeholder="输入AI服务商的API密钥"
              type="password"
              show-password
            />
          </el-form-item>
        </template>
        
        <el-divider />
        
        <el-form-item>
          <el-button type="primary" @click="saveConfig" :loading="saveLoading">保存设置</el-button>
          <el-button @click="resetConfig">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { configApi } from '../api'
import { ElMessage } from 'element-plus'

export default {
  name: 'SettingsView',
  
  setup() {
    const loading = ref(false)
    const saveLoading = ref(false)
    
    const defaultConfig = {
      proxy_settings: {
        enabled: false,
        url: ''
      },
      llm_settings: {
        enabled: false,
        provider: 'zhipu',
        api_key: ''
      }
    }
    
    const configForm = reactive({...defaultConfig})
    
    // 获取配置
    const fetchConfig = async () => {
      loading.value = true
      try {
        const response = await configApi.getConfig()
        Object.assign(configForm, response.data)
      } catch (error) {
        console.error('获取配置失败:', error)
        ElMessage.error('获取配置失败')
      } finally {
        loading.value = false
      }
    }
    
    // 保存配置
    const saveConfig = async () => {
      saveLoading.value = true
      try {
        await configApi.updateConfig(configForm)
        ElMessage.success('保存成功')
      } catch (error) {
        console.error('保存配置失败:', error)
        ElMessage.error('保存配置失败')
      } finally {
        saveLoading.value = false
      }
    }
    
    // 重置配置
    const resetConfig = () => {
      fetchConfig()
    }
    
    onMounted(() => {
      fetchConfig()
    })
    
    return {
      loading,
      saveLoading,
      configForm,
      saveConfig,
      resetConfig
    }
  }
}
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h3 {
  margin-top: 0;
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: #999;
  line-height: 1.5;
  margin-top: 5px;
  display: block;
}
</style> 