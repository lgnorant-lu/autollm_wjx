# API参考文档

本文档详细说明问卷星自动化系统提供的API接口，供开发者集成和扩展系统功能。

## 1. API概述

### 1.1 基本信息

- **基础URL**: `http://your-api-domain/api/v1`
- **响应格式**: JSON
- **认证方式**: 基本认证(Basic Auth)或API密钥
- **版本控制**: 通过URL路径区分版本(如`/api/v1/`)

### 1.2 通用响应格式

所有API响应均使用统一的JSON格式：

```json
{
  "status": "success",  // 或 "error"
  "message": "操作描述信息",
  "data": {  // 具体数据内容，成功时返回
    ...
  },
  "error": {  // 错误详情，失败时返回
    "code": "错误代码",
    "detail": "详细错误信息"
  }
}
```

### 1.3 认证方法

#### 基本认证

在HTTP请求头中添加Authorization字段：

```
Authorization: Basic base64(username:password)
```

#### API密钥认证

在HTTP请求头中添加API密钥：

```
X-API-Key: your_api_key
```

## 2. 问卷相关API

### 2.1 获取问卷列表

获取系统中的问卷列表。

- **URL**: `/surveys`
- **方法**: `GET`
- **参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|------|------|
| page | Integer | 否 | 页码，默认为1 |
| limit | Integer | 否 | 每页记录数，默认为20 |
| status | String | 否 | 问卷状态过滤（parsed/invalid） |

- **响应示例**:

```json
{
  "status": "success",
  "message": "获取问卷列表成功",
  "data": {
    "total": 25,
    "page": 1,
    "limit": 20,
    "surveys": [
      {
        "id": "survey_001",
        "title": "用户满意度调查",
        "url": "https://www.wjx.cn/vm/example1.aspx",
        "questions_count": 10,
        "created_at": "2023-10-15T08:30:00Z",
        "status": "parsed"
      },
      {
        "id": "survey_002",
        "title": "产品反馈问卷",
        "url": "https://www.wjx.cn/vm/example2.aspx",
        "questions_count": 15,
        "created_at": "2023-10-16T09:45:00Z",
        "status": "parsed"
      }
    ]
  }
}
```

### 2.2 解析新问卷

解析一个新的问卷星问卷。

- **URL**: `/surveys`
- **方法**: `POST`
- **Content-Type**: `application/json`
- **请求体**:

```json
{
  "url": "https://www.wjx.cn/vm/example.aspx"
}
```

- **响应示例**:

```json
{
  "status": "success",
  "message": "问卷解析成功",
  "data": {
    "id": "survey_003",
    "title": "新用户调研",
    "url": "https://www.wjx.cn/vm/example.aspx",
    "questions_count": 12,
    "created_at": "2023-10-18T14:20:00Z",
    "status": "parsed"
  }
}
```

### 2.3 获取问卷详情

获取特定问卷的详细信息。

- **URL**: `/surveys/{id}`
- **方法**: `GET`
- **参数**: 无

- **响应示例**:

```json
{
  "status": "success",
  "message": "获取问卷详情成功",
  "data": {
    "id": "survey_001",
    "title": "用户满意度调查",
    "url": "https://www.wjx.cn/vm/example1.aspx",
    "created_at": "2023-10-15T08:30:00Z",
    "status": "parsed",
    "questions": [
      {
        "id": "q1",
        "type": "single_choice",
        "title": "您的性别是？",
        "required": true,
        "options": [
          {"id": "q1_1", "text": "男"},
          {"id": "q1_2", "text": "女"}
        ]
      },
      {
        "id": "q2",
        "type": "multiple_choice",
        "title": "您使用过以下哪些产品？",
        "required": true,
        "options": [
          {"id": "q2_1", "text": "产品A"},
          {"id": "q2_2", "text": "产品B"},
          {"id": "q2_3", "text": "产品C"},
          {"id": "q2_4", "text": "产品D"}
        ]
      }
    ]
  }
}
```

### 2.4 删除问卷

删除系统中的一个问卷。

- **URL**: `/surveys/{id}`
- **方法**: `DELETE`
- **参数**: 无

- **响应示例**:

```json
{
  "status": "success",
  "message": "问卷删除成功",
  "data": {
    "id": "survey_001"
  }
}
```

## 3. 任务相关API

### 3.1 获取任务列表

获取系统中的任务列表。

- **URL**: `/tasks`
- **方法**: `GET`
- **参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|------|------|
| page | Integer | 否 | 页码，默认为1 |
| limit | Integer | 否 | 每页记录数，默认为20 |
| status | String | 否 | 任务状态过滤（waiting/running/completed/stopped/failed） |

- **响应示例**:

```json
{
  "status": "success",
  "message": "获取任务列表成功",
  "data": {
    "total": 15,
    "page": 1,
    "limit": 20,
    "tasks": [
      {
        "id": "task_001",
        "survey_id": "survey_001",
        "survey_title": "用户满意度调查",
        "created_at": "2023-10-16T10:30:00Z",
        "status": "completed",
        "total_count": 100,
        "success_count": 98,
        "failed_count": 2
      },
      {
        "id": "task_002",
        "survey_id": "survey_002",
        "survey_title": "产品反馈问卷",
        "created_at": "2023-10-17T14:20:00Z",
        "status": "running",
        "total_count": 50,
        "success_count": 28,
        "failed_count": 0
      }
    ]
  }
}
```

### 3.2 创建新任务

创建一个新的问卷提交任务。

- **URL**: `/tasks`
- **方法**: `POST`
- **Content-Type**: `application/json`
- **请求体**:

```json
{
  "survey_id": "survey_001",
  "count": 50,
  "settings": {
    "frequency": 5,  // 每分钟提交次数
    "use_proxy": true,  // 是否使用代理
    "answer_mode": "ai",  // random/fixed/ai
    "answer_rules": {
      "q1": {"fixed": "q1_1"},  // 固定选择第一个选项
      "q2": {"min_select": 2, "max_select": 3}  // 随机选择2-3个选项
    }
  }
}
```

- **响应示例**:

```json
{
  "status": "success",
  "message": "任务创建成功",
  "data": {
    "id": "task_003",
    "survey_id": "survey_001",
    "survey_title": "用户满意度调查",
    "created_at": "2023-10-18T16:40:00Z",
    "status": "waiting",
    "total_count": 50,
    "success_count": 0,
    "failed_count": 0
  }
}
```

### 3.3 获取任务详情

获取特定任务的详细信息。

- **URL**: `/tasks/{id}`
- **方法**: `GET`
- **参数**: 无

- **响应示例**:

```json
{
  "status": "success",
  "message": "获取任务详情成功",
  "data": {
    "id": "task_001",
    "survey_id": "survey_001",
    "survey_title": "用户满意度调查",
    "created_at": "2023-10-16T10:30:00Z",
    "updated_at": "2023-10-16T11:45:00Z",
    "status": "completed",
    "total_count": 100,
    "success_count": 98,
    "failed_count": 2,
    "settings": {
      "frequency": 5,
      "use_proxy": true,
      "answer_mode": "ai",
      "answer_rules": {
        "q1": {"fixed": "q1_1"},
        "q2": {"min_select": 2, "max_select": 3}
      }
    },
    "recent_submissions": [
      {
        "id": "sub_098",
        "created_at": "2023-10-16T11:44:30Z",
        "status": "success"
      },
      {
        "id": "sub_099",
        "created_at": "2023-10-16T11:44:45Z",
        "status": "success"
      },
      {
        "id": "sub_100",
        "created_at": "2023-10-16T11:45:00Z",
        "status": "success"
      }
    ]
  }
}
```

### 3.4 更新任务状态

更新任务的状态（启动、暂停、停止任务）。

- **URL**: `/tasks/{id}/status`
- **方法**: `PUT`
- **Content-Type**: `application/json`
- **请求体**:

```json
{
  "status": "running"  // waiting/running/stopped
}
```

- **响应示例**:

```json
{
  "status": "success",
  "message": "任务状态更新成功",
  "data": {
    "id": "task_002",
    "status": "running",
    "updated_at": "2023-10-18T17:20:00Z"
  }
}
```

### 3.5 删除任务

删除系统中的一个任务。

- **URL**: `/tasks/{id}`
- **方法**: `DELETE`
- **参数**: 无

- **响应示例**:

```json
{
  "status": "success",
  "message": "任务删除成功",
  "data": {
    "id": "task_001"
  }
}
```

## 4. 提交结果API

### 4.1 获取提交列表

获取特定任务的提交结果列表。

- **URL**: `/tasks/{task_id}/submissions`
- **方法**: `GET`
- **参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|------|------|
| page | Integer | 否 | 页码，默认为1 |
| limit | Integer | 否 | 每页记录数，默认为20 |
| status | String | 否 | 状态过滤（success/failed） |

- **响应示例**:

```json
{
  "status": "success",
  "message": "获取提交列表成功",
  "data": {
    "total": 98,
    "page": 1,
    "limit": 20,
    "submissions": [
      {
        "id": "sub_001",
        "task_id": "task_001",
        "created_at": "2023-10-16T10:35:00Z",
        "status": "success",
        "submission_time": 2.3  // 秒
      },
      {
        "id": "sub_002",
        "task_id": "task_001",
        "created_at": "2023-10-16T10:35:12Z",
        "status": "success",
        "submission_time": 1.8
      }
    ]
  }
}
```

### 4.2 获取提交详情

获取特定提交的详细信息。

- **URL**: `/submissions/{id}`
- **方法**: `GET`
- **参数**: 无

- **响应示例**:

```json
{
  "status": "success",
  "message": "获取提交详情成功",
  "data": {
    "id": "sub_001",
    "task_id": "task_001",
    "survey_id": "survey_001",
    "created_at": "2023-10-16T10:35:00Z",
    "status": "success",
    "submission_time": 2.3,
    "answers": {
      "q1": "q1_1",
      "q2": ["q2_1", "q2_3"]
    },
    "proxy_used": "123.45.67.89",
    "error": null
  }
}
```

### 4.3 导出提交数据

导出任务的所有提交数据。

- **URL**: `/tasks/{task_id}/export`
- **方法**: `GET`
- **参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|------|------|
| format | String | 否 | 导出格式(csv/json/excel)，默认为csv |
| include_survey_structure | Boolean | 否 | 是否包含问卷结构，默认为false |

- **响应示例**:

返回二进制文件流，用于下载导出的文件。

## 5. 系统配置API

### 5.1 获取系统配置

获取当前系统配置。

- **URL**: `/config`
- **方法**: `GET`
- **参数**: 无

- **响应示例**:

```json
{
  "status": "success",
  "message": "获取系统配置成功",
  "data": {
    "llm": {
      "service": "openai",
      "model": "gpt-3.5-turbo",
      "temperature": 0.7,
      "max_tokens": 500
    },
    "proxy": {
      "enabled": true,
      "source": "internal_pool",
      "rotation_interval": 10
    },
    "submission": {
      "default_frequency": 3,
      "max_frequency": 10,
      "retry_attempts": 3,
      "retry_delay": 5
    },
    "security": {
      "ip_whitelist": ["192.168.1.1", "10.0.0.1"],
      "rate_limit": 100
    }
  }
}
```

### 5.2 更新系统配置

更新系统配置。

- **URL**: `/config`
- **方法**: `PUT`
- **Content-Type**: `application/json`
- **请求体**:

```json
{
  "llm": {
    "service": "openai",
    "model": "gpt-4",
    "temperature": 0.8,
    "max_tokens": 500
  },
  "proxy": {
    "enabled": true,
    "source": "custom",
    "custom_proxies": ["http://proxy1:8080", "http://proxy2:8080"],
    "rotation_interval": 5
  },
  "submission": {
    "default_frequency": 5,
    "max_frequency": 15,
    "retry_attempts": 5,
    "retry_delay": 3
  }
}
```

- **响应示例**:

```json
{
  "status": "success",
  "message": "系统配置更新成功",
  "data": {
    "updated_at": "2023-10-18T18:30:00Z"
  }
}
```

## 6. 错误代码

| 错误代码 | 描述 | HTTP状态码 |
|---------|------|-----------|
| E001 | 无效的问卷URL | 400 |
| E002 | 问卷解析失败 | 400 |
| E003 | 资源不存在 | 404 |
| E004 | 参数验证失败 | 400 |
| E005 | 权限不足 | 403 |
| E006 | 请求过于频繁 | 429 |
| E007 | 内部服务错误 | 500 |
| E008 | 第三方服务不可用 | 502 |
| E009 | 任务状态不允许此操作 | 400 |
| E010 | 认证失败 | 401 |

## 7. 使用示例

### 7.1 Python示例

```python
import requests
import json

# 基本配置
API_BASE_URL = "http://your-api-domain/api/v1"
API_KEY = "your_api_key"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# 解析新问卷
def parse_survey(url):
    response = requests.post(
        f"{API_BASE_URL}/surveys",
        headers=HEADERS,
        data=json.dumps({"url": url})
    )
    return response.json()

# 创建新任务
def create_task(survey_id, count):
    payload = {
        "survey_id": survey_id,
        "count": count,
        "settings": {
            "frequency": 5,
            "use_proxy": True,
            "answer_mode": "random"
        }
    }
    response = requests.post(
        f"{API_BASE_URL}/tasks",
        headers=HEADERS,
        data=json.dumps(payload)
    )
    return response.json()

# 获取任务状态
def get_task_status(task_id):
    response = requests.get(
        f"{API_BASE_URL}/tasks/{task_id}",
        headers=HEADERS
    )
    return response.json()

# 启动任务
def start_task(task_id):
    payload = {"status": "running"}
    response = requests.put(
        f"{API_BASE_URL}/tasks/{task_id}/status",
        headers=HEADERS,
        data=json.dumps(payload)
    )
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 1. 解析问卷
    survey_url = "https://www.wjx.cn/vm/example.aspx"
    survey_result = parse_survey(survey_url)
    
    if survey_result["status"] == "success":
        survey_id = survey_result["data"]["id"]
        print(f"问卷解析成功，ID: {survey_id}")
        
        # 2. 创建提交任务
        task_result = create_task(survey_id, 10)
        
        if task_result["status"] == "success":
            task_id = task_result["data"]["id"]
            print(f"任务创建成功，ID: {task_id}")
            
            # 3. 启动任务
            start_result = start_task(task_id)
            
            if start_result["status"] == "success":
                print("任务已启动")
                
                # 4. 轮询任务状态
                import time
                for _ in range(10):
                    time.sleep(5)
                    status_result = get_task_status(task_id)
                    status = status_result["data"]["status"]
                    success = status_result["data"]["success_count"]
                    total = status_result["data"]["total_count"]
                    print(f"任务状态: {status}, 进度: {success}/{total}")
                    
                    if status in ["completed", "stopped", "failed"]:
                        break
            else:
                print(f"启动任务失败: {start_result['message']}")
        else:
            print(f"创建任务失败: {task_result['message']}")
    else:
        print(f"问卷解析失败: {survey_result['message']}")
```

### 7.2 JavaScript示例

```javascript
// 基本配置
const API_BASE_URL = "http://your-api-domain/api/v1";
const API_KEY = "your_api_key";
const HEADERS = {
  "Content-Type": "application/json",
  "X-API-Key": API_KEY
};

// 解析新问卷
async function parseSurvey(url) {
  const response = await fetch(`${API_BASE_URL}/surveys`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({ url })
  });
  return await response.json();
}

// 创建新任务
async function createTask(surveyId, count) {
  const payload = {
    survey_id: surveyId,
    count: count,
    settings: {
      frequency: 5,
      use_proxy: true,
      answer_mode: "random"
    }
  };
  
  const response = await fetch(`${API_BASE_URL}/tasks`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify(payload)
  });
  return await response.json();
}

// 获取任务状态
async function getTaskStatus(taskId) {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: "GET",
    headers: HEADERS
  });
  return await response.json();
}

// 启动任务
async function startTask(taskId) {
  const payload = { status: "running" };
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/status`, {
    method: "PUT",
    headers: HEADERS,
    body: JSON.stringify(payload)
  });
  return await response.json();
}

// 使用示例
async function runExample() {
  try {
    // 1. 解析问卷
    const surveyUrl = "https://www.wjx.cn/vm/example.aspx";
    const surveyResult = await parseSurvey(surveyUrl);
    
    if (surveyResult.status === "success") {
      const surveyId = surveyResult.data.id;
      console.log(`问卷解析成功，ID: ${surveyId}`);
      
      // 2. 创建提交任务
      const taskResult = await createTask(surveyId, 10);
      
      if (taskResult.status === "success") {
        const taskId = taskResult.data.id;
        console.log(`任务创建成功，ID: ${taskId}`);
        
        // 3. 启动任务
        const startResult = await startTask(taskId);
        
        if (startResult.status === "success") {
          console.log("任务已启动");
          
          // 4. 轮询任务状态
          const checkStatus = async () => {
            const statusResult = await getTaskStatus(taskId);
            const { status, success_count, total_count } = statusResult.data;
            console.log(`任务状态: ${status}, 进度: ${success_count}/${total_count}`);
            
            if (["completed", "stopped", "failed"].includes(status)) {
              console.log("任务结束");
              return;
            }
            
            // 继续轮询
            setTimeout(checkStatus, 5000);
          };
          
          checkStatus();
        } else {
          console.log(`启动任务失败: ${startResult.message}`);
        }
      } else {
        console.log(`创建任务失败: ${taskResult.message}`);
      }
    } else {
      console.log(`问卷解析失败: ${surveyResult.message}`);
    }
  } catch (error) {
    console.error("API调用出错:", error);
  }
}

runExample();
```

## 8. 附录

### 8.1 支持的问卷题型

| 类型标识 | 描述 |
|----------|------|
| single_choice | 单选题 |
| multiple_choice | 多选题 |
| fill_blank | 填空题 |
| dropdown | 下拉选择题 |
| matrix_single | 矩阵单选题 |
| matrix_multiple | 矩阵多选题 |
| matrix_fill | 矩阵填空题 |
| scale | 量表题 |
| sorting | 排序题 |
| date | 日期题 |

### 8.2 API变更日志

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2023-01-15 | 初始API发布 |
| v1.1 | 2023-03-20 | 添加AI辅助填写相关接口 |
| v1.2 | 2023-06-08 | 增强代理IP管理功能 |
| v1.3 | 2023-09-12 | 添加数据导出接口 |