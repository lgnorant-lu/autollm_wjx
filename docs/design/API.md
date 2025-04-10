# API设计文档

本文档定义问卷星自动化系统的API设计规范和接口定义。

## 1. RESTful API设计原则

系统API采用RESTful设计风格，遵循以下原则：

- 使用HTTP动词表示操作(GET, POST, PUT, DELETE)
- 资源使用名词复数形式
- 版本号包含在URL中
- 使用HTTP状态码表示请求结果
- 支持分页和过滤

## 2. 主要API端点

### 2.1 问卷相关

| 方法 | 路径 | 描述 | 请求参数 | 响应 |
|------|------|------|----------|------|
| GET | /api/v1/surveys | 获取问卷列表 | page, limit, status | 问卷列表 |
| POST | /api/v1/surveys | 解析新问卷 | url | 问卷详情 |
| GET | /api/v1/surveys/{id} | 获取问卷详情 | id | 问卷详情 |
| DELETE | /api/v1/surveys/{id} | 删除问卷 | id | 操作结果 |

```
GET    /api/v1/surveys                # 获取问卷列表
POST   /api/v1/surveys                # 解析新问卷
GET    /api/v1/surveys/{id}           # 获取问卷详情
DELETE /api/v1/surveys/{id}           # 删除问卷
```

### 2.2 任务相关

| 方法 | 路径 | 描述 | 请求参数 | 响应 |
|------|------|------|----------|------|
| GET | /api/v1/tasks | 获取任务列表 | page, limit, status | 任务列表 |
| POST | /api/v1/tasks | 创建新任务 | survey_id, count, settings | 任务详情 |
| GET | /api/v1/tasks/{id} | 获取任务详情 | id | 任务详情 |
| PUT | /api/v1/tasks/{id}/status | 更新任务状态 | id, status | 操作结果 |
| DELETE | /api/v1/tasks/{id} | 删除任务 | id | 操作结果 |

```
GET    /api/v1/tasks                  # 获取任务列表
POST   /api/v1/tasks                  # 创建新任务
GET    /api/v1/tasks/{id}             # 获取任务详情
PUT    /api/v1/tasks/{id}/status      # 更新任务状态
DELETE /api/v1/tasks/{id}             # 删除任务
```

### 2.3 系统配置相关

| 方法 | 路径 | 描述 | 请求参数 | 响应 |
|------|------|------|----------|------|
| GET | /api/v1/config | 获取当前配置 | - | 系统配置 |
| PUT | /api/v1/config | 更新配置 | config_data | 更新后的配置 |

```
GET    /api/v1/config                 # 获取当前配置
PUT    /api/v1/config                 # 更新配置
```

## 3. 数据格式

所有API均使用JSON格式进行数据交换，例如：

### 请求示例

```json
POST /api/v1/tasks
{
  "survey_id": "survey-123",
  "count": 50,
  "settings": {
    "interval": [3, 10],
    "proxy_enabled": true,
    "answer_diversity": "high"
  }
}
```

### 响应示例

```json
{
  "status": "success",
  "data": {
    "id": "task-123",
    "type": "submit",
    "status": "running",
    "progress": 45,
    "created_at": "2025-03-28T12:34:56Z"
  }
}
```

### 错误响应

```json
{
  "status": "error",
  "error": {
    "code": "not_found",
    "message": "Survey not found"
  }
}
```

## 4. API安全性

### 4.1 认证

当前版本使用基本认证机制，未来将支持以下认证方式：

- API密钥认证
- OAuth 2.0认证

### 4.2 安全措施

- 使用HTTPS加密传输
- 实现请求频率限制，防止DDoS攻击
- 设置请求超时时间
- 实现IP白名单（可选）
- 敏感信息加密存储

## 5. API版本管理

API版本通过URL路径进行管理，例如`/api/v1/...`。当API有不兼容变更时，将创建新版本，同时保持旧版本一段时间以便客户端平滑迁移。 