# 变更日志索引

本文档索引问卷星自动化系统的所有变更记录，详细变更日志存储在`docs/logs`目录下。

## 1. 版本更新日志

| 版本 | 发布日期 | 变更说明 | 详细日志 |
|------|----------|---------|---------|
| v1.0 Beta | 2023-12-01 | 首个测试版本发布 | [v1.0-beta.md](../logs/releases/v1.0-beta.md) |
| v1.0 RC | 2024-01-15 | 发布候选版本 | [v1.0-rc.md](../logs/releases/v1.0-rc.md) |
| v1.0 | 2024-02-15 | 稳定版发布 | [v1.0.md](../logs/releases/v1.0.md) |
| v1.1 RC | 2024-03-28 | 部署优化版候选发布 | [v1.1-rc.md](../logs/releases/v1.1-rc.md) |

## 2. 模块变更日志

### 2.1 后端模块

| 模块 | 最近更新 | 变更说明 | 详细日志 |
|------|----------|---------|---------|
| 测试模块 | 2025-04-18 | 添加参数化测试脚本 | [update_2025_04_18.md](../logs/update_2025_04_18.md) |
| 核心解析器 | 2024-01-10 | 修复特殊题型解析问题 | [parser-update-20240110.md](../logs/backend/parser-update-20240110.md) |
| 提交引擎 | 2024-01-08 | 开始IP代理管理优化 | [submitter-update-20240108.md](../logs/backend/submitter-update-20240108.md) |
| 任务管理 | 2023-12-05 | 实现任务暂停/继续功能 | [task-manager-update-20231205.md](../logs/backend/task-manager-update-20231205.md) |
| AI生成器 | 2023-12-20 | 优化填空题答案生成 | [ai-generator-update-20231220.md](../logs/backend/ai-generator-update-20231220.md) |
| API接口 | 2023-12-15 | 完善错误处理和响应格式 | [api-update-20231215.md](../logs/backend/api-update-20231215.md) |

### 2.2 前端模块

| 模块 | 最近更新 | 变更说明 | 详细日志 |
|------|----------|---------|---------|
| 图表组件 | 2025-04-18 | 优化提交时间分布图 | [update_2025_04_18.md](../logs/update_2025_04_18.md) |
| 分页功能 | 2025-04-18 | 修复分页问题 | [update_2025_04_18.md](../logs/update_2025_04_18.md) |
| 问卷管理 | 2024-01-05 | 优化问卷详情展示 | [survey-ui-update-20240105.md](../logs/frontend/survey-ui-update-20240105.md) |
| 任务管理 | 2024-01-14 | 改进任务创建表单 | [task-ui-update-20240114.md](../logs/frontend/task-ui-update-20240114.md) |
| 系统设置 | 2023-12-12 | 添加系统配置界面 | [settings-ui-update-20231212.md](../logs/frontend/settings-ui-update-20231212.md) |
| UI组件 | 2023-12-20 | 统一组件风格，提升响应式支持 | [ui-components-update-20231220.md](../logs/frontend/ui-components-update-20231220.md) |

### 2.3 部署模块

| 模块 | 最近更新 | 变更说明 | 详细日志 |
|------|----------|---------|---------|
| 部署脚本 | 2024-03-28 | 添加Windows PowerShell部署脚本 | [deploy-update-20240328.md](../logs/deployment/deploy-update-20240328.md) |
| 一键部署工具 | 2024-03-28 | 创建Windows一键部署批处理文件 | [setup-update-20240328.md](../logs/deployment/setup-update-20240328.md) |
| Docker配置 | 2024-03-25 | 优化Docker镜像构建配置 | [docker-update-20240325.md](../logs/deployment/docker-update-20240325.md) |

## 3. 重要变更摘要

### 3.1 架构变更

| 日期 | 变更说明 | 详细日志 |
|------|---------|---------|
| 2025-04-18 | 整合测试脚本，添加参数化测试 | [update_2025_04_18.md](../logs/update_2025_04_18.md) |
| 2023-12-05 | 重构数据存储结构 | [architecture-update-20231205.md](../logs/architecture/architecture-update-20231205.md) |
| 2023-12-15 | 优化API接口设计 | [api-design-update-20231215.md](../logs/architecture/api-design-update-20231215.md) |

### 3.2 安全更新

| 日期 | 变更说明 | 详细日志 |
|------|---------|---------|
| 2024-01-10 | 开始配置文件敏感信息加密 | [security-update-20240110.md](../logs/security/security-update-20240110.md) |
| 2023-12-20 | 增强登录认证机制 | [auth-update-20231220.md](../logs/security/auth-update-20231220.md) |

### 3.3 性能优化

| 日期 | 变更说明 | 详细日志 |
|------|---------|---------|
| 2024-01-10 | 开始优化大型问卷解析性能 | [performance-parser-20240110.md](../logs/performance/performance-parser-20240110.md) |
| 2023-12-10 | 优化任务执行效率 | [performance-task-20231210.md](../logs/performance/performance-task-20231210.md) |

### 3.4 部署优化

| 日期 | 变更说明 | 详细日志 |
|------|---------|---------|
| 2024-03-28 | 实现Windows环境完整部署解决方案 | [deploy-windows-20240328.md](../logs/deployment/deploy-windows-20240328.md) |
| 2024-03-28 | 优化项目文件结构 | [project-structure-20240328.md](../logs/deployment/project-structure-20240328.md) |
| 2024-03-25 | 优化Docker镜像构建流程 | [docker-optimization-20240325.md](../logs/deployment/docker-optimization-20240325.md) |

## 4. 待发布变更

以下变更已完成但尚未发布到生产环境：

| 变更 | 开发完成日期 | 计划发布日期 | 关联任务 |
|------|------------|------------|---------|
| 任务自动重试机制 | 进行中 | 2024-04-05 | T2401-07 |
| API接口速率限制 | 进行中 | 2024-04-05 | T2401-08 |
| CSV导出中文编码修复 | 进行中 | 2024-04-10 | T2401-09 |
| Windows部署脚本 | 2024-03-28 | 2024-03-30 | T2403-00, T2403-01 |

## 5. 变更日志格式指南

### 5.1 发布日志格式

```markdown
# 版本 v1.x.x

发布日期：YYYY-MM-DD

## 新增功能

- 功能1描述
- 功能2描述

## 改进

- 改进1描述
- 改进2描述

## 修复问题

- 修复问题1描述
- 修复问题2描述

## 已知问题

- 已知问题1描述
- 已知问题2描述

## 贡献者

- lgnorant-lu
- Yong-dao
- ming
```

### 5.2 模块变更日志格式

```markdown
# 模块名称变更 - YYYY-MM-DD

## 变更摘要

简要描述本次变更的主要内容

## 详细变更

### 新增功能

- 新增功能1
- 新增功能2

### 代码变更

- 修改了文件X，实现了功能Y
- 重构了模块Z

### 测试情况

- 单元测试覆盖率: XX%
- 已通过的测试: 测试1, 测试2

## 注意事项

使用该模块时需要注意的事项

## 负责人

- 开发者: lgnorant-lu
- 审阅者: Yong-dao
- 测试: ming
```