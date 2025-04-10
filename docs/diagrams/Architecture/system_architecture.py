#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表名称: 系统架构图
创建日期: 2023-12-01
最后更新: 2023-12-01
描述: 展示问卷星自动化系统的整体架构和主要组件
"""

import graphviz

# 创建图表
dot = graphviz.Digraph('System Architecture', 
                      comment='问卷星自动化系统架构图',
                      format='png')
dot.attr(rankdir='TB', size='8,5', dpi='300')

# 创建子图 - 前端层
with dot.subgraph(name='cluster_frontend') as c:
    c.attr(label='前端层', style='filled', color='lightblue')
    c.node('vue_app', 'Vue.js应用', shape='box')
    c.node('ui_components', 'UI组件库', shape='box')
    c.node('api_client', 'API客户端', shape='box')
    c.node('state_mgmt', '状态管理(Vuex)', shape='box')
    
    c.edge('vue_app', 'ui_components')
    c.edge('vue_app', 'api_client')
    c.edge('vue_app', 'state_mgmt')

# 创建子图 - 后端API层
with dot.subgraph(name='cluster_api') as c:
    c.attr(label='后端API层', style='filled', color='lightgreen')
    c.node('flask_app', 'Flask应用', shape='box')
    c.node('api_routes', 'API路由', shape='box')
    c.node('auth', '认证授权', shape='box')
    c.node('validators', '输入验证', shape='box')
    
    c.edge('flask_app', 'api_routes')
    c.edge('api_routes', 'auth')
    c.edge('api_routes', 'validators')

# 创建子图 - 核心功能层
with dot.subgraph(name='cluster_core') as c:
    c.attr(label='核心功能层', style='filled', color='lightyellow')
    c.node('parser', '问卷解析模块', shape='box')
    c.node('generator', '答案生成模块', shape='box')
    c.node('submitter', '问卷提交模块', shape='box')
    c.node('task_mgr', '任务管理模块', shape='box')
    
    c.edge('task_mgr', 'parser')
    c.edge('task_mgr', 'generator')
    c.edge('task_mgr', 'submitter')
    c.edge('parser', 'generator')
    c.edge('generator', 'submitter')

# 创建子图 - 存储层
with dot.subgraph(name='cluster_storage') as c:
    c.attr(label='数据存储层', style='filled', color='lightpink')
    c.node('data_mgr', '数据管理器', shape='box')
    c.node('file_system', '文件系统存储', shape='cylinder')
    
    c.edge('data_mgr', 'file_system')

# 创建外部系统
dot.node('wjx', '问卷星平台', shape='box3d', style='filled', fillcolor='lightgrey')
dot.node('llm_api', 'LLM API服务', shape='box3d', style='filled', fillcolor='lightgrey')

# 连接各层
dot.edge('api_client', 'flask_app', label='HTTP/REST')
dot.edge('api_routes', 'task_mgr')
dot.edge('api_routes', 'data_mgr')
dot.edge('task_mgr', 'data_mgr')
dot.edge('parser', 'data_mgr')
dot.edge('submitter', 'wjx', label='HTTP')
dot.edge('generator', 'llm_api', label='API调用')

# 保存图表
dot.render('system_architecture', directory='./output', cleanup=True)
print("图表已生成: ./output/system_architecture.png") 