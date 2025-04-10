#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表名称: 模块依赖关系图
创建日期: 2023-12-15
最后更新: 2023-12-15
描述: 展示问卷星自动化系统各模块间的依赖关系
"""

import graphviz

# 创建图表
dot = graphviz.Digraph('Module Dependencies', 
                      comment='问卷星自动化系统模块依赖关系图',
                      format='png')
dot.attr(rankdir='TB', size='10,8', dpi='300')

# 设置节点默认样式
dot.attr('node', shape='box', style='filled', color='black', fontname='Arial')

# 定义模块组
api_modules = {
    'api_surveys': ('surveys.py', 'lightblue'),
    'api_tasks': ('tasks.py', 'lightblue'),
    'api_submissions': ('submissions.py', 'lightblue'),
    'api_config': ('config.py', 'lightblue'),
}

core_modules = {
    'parser': ('parser模块', 'lightyellow'),
    'generator': ('generator模块', 'lightyellow'),
    'submitter': ('submitter模块', 'lightyellow'),
    'task_manager': ('task_manager.py', 'lightyellow'),
    'survey_manager': ('survey_manager.py', 'lightyellow'),
    'data_manager': ('data_manager.py', 'lightyellow'),
}

util_modules = {
    'logger': ('logger.py', 'lightgreen'),
    'file_utils': ('file_utils.py', 'lightgreen'),
    'http_utils': ('http_utils.py', 'lightgreen'),
    'security': ('security.py', 'lightgreen'),
    'validators': ('validators.py', 'lightgreen'),
}

external_deps = {
    'flask': ('Flask', 'lightgrey'),
    'bs4': ('BeautifulSoup', 'lightgrey'),
    'requests': ('Requests', 'lightgrey'),
    'llm_api': ('LLM API', 'lightgrey'),
}

# 添加节点
for module_id, (name, color) in {**api_modules, **core_modules, **util_modules, **external_deps}.items():
    dot.node(module_id, name, fillcolor=color)

# 添加子模块
# 解析器子模块
with dot.subgraph(name='cluster_parser') as c:
    c.attr(label='parser模块', style='filled', fillcolor='lightyellow')
    c.node('wjx_parser', 'wjx_parser.py')
    c.node('question_extractor', 'question_extractor.py')
    c.node('html_utils', 'html_utils.py')

# 生成器子模块
with dot.subgraph(name='cluster_generator') as c:
    c.attr(label='generator模块', style='filled', fillcolor='lightyellow')
    c.node('answer_generator', 'answer_generator.py')
    c.node('random_generator', 'random_generator.py')
    c.node('fixed_generator', 'fixed_generator.py')
    c.node('ai_generator', 'ai_generator.py')

# 提交器子模块
with dot.subgraph(name='cluster_submitter') as c:
    c.attr(label='submitter模块', style='filled', fillcolor='lightyellow')
    c.node('submitter_base', 'submitter.py')
    c.node('wjx_submitter', 'wjx_submitter.py')
    c.node('proxy_manager', 'proxy_manager.py')

# 添加API依赖关系
dot.edge('api_surveys', 'survey_manager')
dot.edge('api_surveys', 'validators')
dot.edge('api_tasks', 'task_manager')
dot.edge('api_tasks', 'validators')
dot.edge('api_submissions', 'task_manager')
dot.edge('api_config', 'data_manager')
dot.edge('api_config', 'security')

# 添加核心模块依赖关系
dot.edge('survey_manager', 'parser')
dot.edge('survey_manager', 'data_manager')
dot.edge('task_manager', 'survey_manager')
dot.edge('task_manager', 'generator')
dot.edge('task_manager', 'submitter')
dot.edge('task_manager', 'data_manager')
dot.edge('parser', 'http_utils')
dot.edge('generator', 'file_utils')
dot.edge('submitter', 'http_utils')
dot.edge('data_manager', 'file_utils')

# 添加子模块依赖关系
dot.edge('wjx_parser', 'question_extractor')
dot.edge('wjx_parser', 'html_utils')
dot.edge('question_extractor', 'html_utils')
dot.edge('random_generator', 'answer_generator')
dot.edge('fixed_generator', 'answer_generator')
dot.edge('ai_generator', 'answer_generator')
dot.edge('ai_generator', 'llm_api')
dot.edge('wjx_submitter', 'submitter_base')
dot.edge('wjx_submitter', 'proxy_manager')

# 添加工具依赖关系
for module in list(api_modules.keys()) + list(core_modules.keys()):
    dot.edge(module, 'logger')

# 添加外部依赖关系
for api_module in api_modules.keys():
    dot.edge(api_module, 'flask')
dot.edge('http_utils', 'requests')
dot.edge('wjx_parser', 'bs4')

# 保存图表
dot.render('module_dependencies', directory='./output', cleanup=True)
print("图表已生成: ./output/module_dependencies.png") 