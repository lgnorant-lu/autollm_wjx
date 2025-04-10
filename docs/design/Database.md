# 数据模型设计文档

本文档描述问卷星自动化系统的数据模型和存储结构。

## 1. 数据存储概述

系统使用文件系统进行数据存储，主要使用JSON格式文件。这种设计具有以下优势：

- 简化部署，避免数据库依赖
- 便于数据备份和迁移
- 适合中小规模应用场景
- 符合系统轻量化设计理念

## 2. 主要数据结构

### 2.1 问卷数据结构

问卷数据存储在`data/surveys/{survey_id}.json`中，结构如下：

```json
{
  "id": "survey-123",
  "title": "用户满意度调查",
  "url": "https://www.wjx.cn/vm/abcdef.aspx",
  "created_at": "2025-03-28T10:30:00Z",
  "updated_at": "2025-03-28T10:30:00Z",
  "status": "active",
  "metadata": {
    "creator": "system",
    "creator_ip": "127.0.0.1",
    "parse_time": 1.25
  },
  "questions": [
    {
      "id": 1,
      "type": "single_choice",
      "title": "您的性别是？",
      "required": true,
      "options": [
        {"id": 1, "text": "男"},
        {"id": 2, "text": "女"}
      ]
    },
    {
      "id": 2,
      "type": "multiple_choice",
      "title": "您使用过哪些社交媒体平台？",
      "required": true,
      "options": [
        {"id": 1, "text": "微信"},
        {"id": 2, "text": "微博"},
        {"id": 3, "text": "抖音"},
        {"id": 4, "text": "知乎"},
        {"id": 5, "text": "其他"}
      ]
    },
    {
      "id": 3,
      "type": "text",
      "title": "您对我们的产品有什么建议？",
      "required": false
    }
  ],
  "original_html": "base64_encoded_html_content"
}
```

### 2.2 任务数据结构

任务数据存储在`data/tasks/{task_id}.json`中，结构如下：

```json
{
  "id": "task-456",
  "survey_id": "survey-123",
  "created_at": "2025-03-28T14:20:00Z",
  "updated_at": "2025-03-28T15:30:45Z",
  "status": "running", // pending, running, paused, completed, failed
  "progress": 65,
  "settings": {
    "total_count": 100,
    "completed_count": 65,
    "failed_count": 3,
    "interval": [5, 15],
    "proxy_enabled": true,
    "answer_diversity": "high"
  },
  "submissions": [
    {
      "id": "sub-001",
      "status": "success",
      "submitted_at": "2025-03-28T14:25:32Z",
      "response_id": "wjx-resp-12345",
      "proxy_used": "123.45.67.89",
      "answers": [{"q_id": 1, "value": 1}, {"q_id": 2, "value": [1, 3, 4]}, {"q_id": 3, "value": "产品很好用，希望增加更多功能"}]
    },
    // ...更多提交记录
  ]
}
```

### 2.3 系统配置数据结构

系统配置存储在`data/system_config.json`中，结构如下：

```json
{
  "updated_at": "2025-03-28T09:00:00Z",
  "llm": {
    "provider": "openai",
    "api_key": "encrypted_api_key",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500
  },
  "proxy": {
    "enabled": true,
    "sources": ["file", "api"],
    "file_path": "data/proxy_list.txt",
    "api_url": "https://proxy-provider.com/api",
    "api_key": "encrypted_api_key",
    "rotation_strategy": "round_robin"
  },
  "submission": {
    "max_concurrent": 5,
    "default_interval": [3, 10],
    "retry_count": 3,
    "timeout": 30
  },
  "security": {
    "api_keys": ["encrypted_key_1", "encrypted_key_2"],
    "allowed_ips": ["127.0.0.1", "192.168.1.0/24"]
  }
}
```

### 2.4 索引数据结构

为了提高查询效率，系统维护了几个索引文件：

#### 问卷索引 (`data/survey_index.json`)

```json
{
  "updated_at": "2025-03-28T16:00:00Z",
  "surveys": [
    {
      "id": "survey-123",
      "title": "用户满意度调查",
      "created_at": "2025-03-28T10:30:00Z",
      "status": "active"
    },
    // ...更多问卷索引
  ]
}
```

#### 任务索引 (`data/task_index.json`)

```json
{
  "updated_at": "2025-03-28T16:00:00Z",
  "tasks": [
    {
      "id": "task-456",
      "survey_id": "survey-123",
      "created_at": "2025-03-28T14:20:00Z",
      "status": "running",
      "progress": 65
    },
    // ...更多任务索引
  ]
}
```

## 3. 数据关系图

![数据模型关系图](../../Diagrams/DataModels/data_relationships.png)

## 4. 数据操作机制

系统实现了以下数据操作机制：

- **事务机制**: 通过文件锁和临时文件实现简单的事务
- **索引更新**: 当主数据更新时，同步更新相关索引
- **备份策略**: 定期自动备份数据目录
- **数据清理**: 自动清理过期数据，避免空间浪费

## 5. 扩展性考虑

尽管当前使用文件系统存储，但系统设计了抽象的数据访问层，便于未来迁移到其他数据库系统：

- MongoDB: 适合存储问卷和任务的文档结构
- Redis: 可用于缓存和任务队列
- SQLite: 轻量级关系型数据库，适合嵌入式部署

## 6. 性能优化

为提高文件系统存储性能，系统采用了以下措施：

- 索引文件加速查询
- 内存缓存常用数据
- 文件分目录存储，避免单目录文件过多
- 批量读写，减少I/O操作
- 延迟写入非关键数据 