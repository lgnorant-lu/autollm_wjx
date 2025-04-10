# 图表索引文档

本文档索引问卷星自动化系统的所有图表，包括架构图、流程图、数据模型图等。所有图表源文件存储在`docs/diagrams`目录下。

## 1. 架构图

| 图表名称 | 最后更新 | 描述 | 文件路径 |
|---------|---------|------|---------|
| 系统整体架构图 | 2023-12-01 | 展示系统的整体架构和主要组件 | [system_architecture.py](../diagrams/Architecture/system_architecture.py) |
| 分层架构图 | 2023-12-05 | 展示系统的分层结构和层间关系 | [layered_architecture.py](../diagrams/Architecture/layered_architecture.py) |
| 部署架构图 | 2024-03-28 | 展示系统的部署方案和组件分布 | [deployment_architecture.py](../diagrams/Architecture/deployment_architecture.py) |
| Windows部署架构图 | 2024-03-28 | 展示Windows环境下的部署架构 | [windows_deployment.py](../diagrams/Architecture/windows_deployment.py) |
| 后端组件关系图 | 2024-01-05 | 展示后端各组件间的依赖关系 | [backend_components.py](../diagrams/Architecture/backend_components.py) |
| 前端组件关系图 | 2024-01-10 | 展示前端各组件间的依赖关系 | [frontend_components.py](../diagrams/Architecture/frontend_components.py) |

## 2. 模块图

| 图表名称 | 最后更新 | 描述 | 文件路径 |
|---------|---------|------|---------|
| 模块依赖关系图 | 2023-12-15 | 展示系统各模块间的依赖关系 | [module_dependencies.py](../diagrams/Modules/module_dependencies.py) |
| 解析器模块结构图 | 2023-12-20 | 展示问卷解析模块的内部结构 | [parser_structure.py](../diagrams/Modules/parser_structure.py) |
| 提交引擎模块结构图 | 2023-12-25 | 展示问卷提交模块的内部结构 | [submitter_structure.py](../diagrams/Modules/submitter_structure.py) |
| 任务管理模块结构图 | 2024-01-05 | 展示任务管理模块的内部结构 | [task_manager_structure.py](../diagrams/Modules/task_manager_structure.py) |
| API模块接口图 | 2024-01-10 | 展示API模块的接口定义 | [api_interface.py](../diagrams/Modules/api_interface.py) |

## 3. 流程图

| 图表名称 | 最后更新 | 描述 | 文件路径 |
|---------|---------|------|---------|
| 问卷解析流程图 | 2023-12-10 | 展示问卷解析的处理流程 | [survey_parsing_flow.py](../diagrams/Flowcharts/survey_parsing_flow.py) |
| 任务创建流程图 | 2023-12-15 | 展示任务创建和初始化流程 | [task_creation_flow.py](../diagrams/Flowcharts/task_creation_flow.py) |
| 问卷提交流程图 | 2023-12-20 | 展示问卷提交的处理流程 | [survey_submission_flow.py](../diagrams/Flowcharts/survey_submission_flow.py) |
| 用户认证流程图 | 2023-12-25 | 展示用户登录和认证流程 | [authentication_flow.py](../diagrams/Flowcharts/authentication_flow.py) |
| 错误处理流程图 | 2024-01-15 | 展示系统错误处理和恢复流程 | [error_handling_flow.py](../diagrams/Flowcharts/error_handling_flow.py) |
| 部署流程图 | 2024-03-28 | 展示系统部署和环境设置流程 | [deployment_flow.py](../diagrams/Flowcharts/deployment_flow.py) |
| Windows部署流程图 | 2024-03-28 | 展示Windows环境的部署流程 | [windows_deployment_flow.py](../diagrams/Flowcharts/windows_deployment_flow.py) |

## 4. 算法图

| 图表名称 | 最后更新 | 描述 | 文件路径 |
|---------|---------|------|---------|
| 问卷解析算法图 | 2023-12-15 | 展示HTML解析和结构提取算法 | [parser_algorithm_flow.py](../diagrams/Algorithms/parser_algorithm_flow.py) |
| 答案生成算法图 | 2023-12-20 | 展示答案生成和优化算法 | [answer_generation_flow.py](../diagrams/Algorithms/answer_generation_flow.py) |
| IP代理选择算法图 | 2024-01-10 | 展示IP代理选择和轮换算法 | [proxy_selection_flow.py](../diagrams/Algorithms/proxy_selection_flow.py) |
| 任务调度算法图 | 2024-01-15 | 展示任务队列管理和调度算法 | [task_scheduling_flow.py](../diagrams/Algorithms/task_scheduling_flow.py) |

## 5. 数据模型图

| 图表名称 | 最后更新 | 描述 | 文件路径 |
|---------|---------|------|---------|
| 实体关系图 | 2023-12-10 | 展示系统主要数据实体及其关系 | [entity_relationship.py](../diagrams/DataModels/entity_relationship.py) |
| 问卷数据结构图 | 2023-12-15 | 展示问卷数据的结构和组织 | [survey_data_structure.py](../diagrams/DataModels/survey_data_structure.py) |
| 任务数据结构图 | 2023-12-20 | 展示任务数据的结构和组织 | [task_data_structure.py](../diagrams/DataModels/task_data_structure.py) |
| 配置数据结构图 | 2023-12-25 | 展示系统配置数据的结构和组织 | [config_data_structure.py](../diagrams/DataModels/config_data_structure.py) |
| 文件存储结构图 | 2024-01-05 | 展示系统文件存储的结构和组织 | [file_storage_structure.py](../diagrams/DataModels/file_storage_structure.py) |

## 6. UI设计图

| 图表名称 | 最后更新 | 描述 | 文件路径 |
|---------|---------|------|---------|
| 页面导航图 | 2023-12-15 | 展示系统页面导航结构 | [page_navigation.py](../diagrams/UI/page_navigation.py) |
| 问卷管理页面设计 | 2023-12-20 | 展示问卷管理页面的布局和组件 | [survey_management_ui.py](../diagrams/UI/survey_management_ui.py) |
| 任务管理页面设计 | 2023-12-25 | 展示任务管理页面的布局和组件 | [task_management_ui.py](../diagrams/UI/task_management_ui.py) |
| 系统设置页面设计 | 2024-01-05 | 展示系统设置页面的布局和组件 | [settings_ui.py](../diagrams/UI/settings_ui.py) |
| 移动端适配设计 | 2024-01-15 | 展示移动端页面的布局和组件 | [mobile_ui.py](../diagrams/UI/mobile_ui.py) |

## 7. 图表生成指南

所有图表使用Python Graphviz库创建，便于版本控制和自动化生成。

### 7.1 安装依赖

```bash
pip install graphviz pydot pylint
```

### 7.2 生成图表

```bash
# 生成单个图表
python docs/diagrams/Architecture/system_architecture.py

# 生成所有图表
python docs/diagrams/generate_all.py
```

### 7.3 图表模板

架构图模板:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表名称: 系统架构图
创建日期: YYYY-MM-DD
最后更新: YYYY-MM-DD
描述: 展示系统的整体架构和主要组件
"""

import graphviz

# 创建图表
dot = graphviz.Digraph('System Architecture', 
                      comment='问卷星自动化系统架构图',
                      format='png')
dot.attr(rankdir='TB', size='8,5', dpi='300')

# 添加节点
dot.node('frontend', '前端应用\n(Vue.js)', shape='box', style='filled', fillcolor='lightblue')
dot.node('backend', '后端服务\n(Flask)', shape='box', style='filled', fillcolor='lightgreen')
dot.node('database', '数据存储\n(JSON文件)', shape='cylinder', style='filled', fillcolor='lightyellow')

# 添加边
dot.edge('frontend', 'backend', label='HTTP/API')
dot.edge('backend', 'database', label='读/写')
dot.edge('backend', 'wjx', label='HTTP请求')

# 保存图表
dot.render('system_architecture', directory='./diagrams/output', cleanup=True)
print("图表已生成: ./diagrams/output/system_architecture.png")
```

### 7.4 图表命名规范

- 文件名使用小写字母和下划线
- 图表输出文件名与源文件名相同，但扩展名为.png
- 图片尺寸建议设置为合适大小，以确保可读性

### 7.5 图表更新流程

1. 修改相应的Python源文件
2. 运行脚本生成图表
3. 提交变更并更新本索引文档中的"最后更新"日期 

## 8. 部署架构图

| 图表名称 | 最后更新 | 描述 | 文件路径 |
|---------|---------|------|---------|
| Docker容器架构图 | 2024-03-25 | 展示系统Docker容器化架构 | [docker_architecture.py](../diagrams/Deployment/docker_architecture.py) |
| Windows部署架构图 | 2024-03-28 | 展示Windows环境部署架构 | [windows_deployment.py](../diagrams/Deployment/windows_deployment.py) |
| Linux部署架构图 | 2024-03-25 | 展示Linux环境部署架构 | [linux_deployment.py](../diagrams/Deployment/linux_deployment.py) |
| 部署组件关系图 | 2024-03-28 | 展示部署脚本与系统组件关系 | [deployment_components.py](../diagrams/Deployment/deployment_components.py) | 