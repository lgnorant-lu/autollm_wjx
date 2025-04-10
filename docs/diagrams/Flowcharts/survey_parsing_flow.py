#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表名称: 问卷解析流程图
创建日期: 2023-12-10
最后更新: 2023-12-10
描述: 展示问卷解析的处理流程
"""

import graphviz

# 创建图表
dot = graphviz.Digraph('Survey Parsing Flow', 
                      comment='问卷星自动化系统问卷解析流程',
                      format='png')
dot.attr(rankdir='TB', size='8,11', dpi='300')

# 添加节点
dot.node('start', '开始', shape='oval', style='filled', fillcolor='lightgreen')
dot.node('input_url', '输入问卷URL', shape='box')
dot.node('validate_url', '验证URL格式', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('fetch_html', '获取问卷HTML内容', shape='box')
dot.node('check_fetch', '检查是否成功获取', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('extract_meta', '提取问卷元数据\n(标题、描述等)', shape='box')
dot.node('extract_questions', '提取问题列表', shape='box')
dot.node('process_questions', '处理问题\n(类型识别、选项提取)', shape='box')
dot.node('check_questions', '检查问题提取是否完整', shape='diamond', style='filled', fillcolor='lightyellow')
dot.node('extract_logic', '提取题目逻辑关系\n(条件、跳转等)', shape='box')
dot.node('build_structure', '构建问卷结构', shape='box')
dot.node('validate_structure', '验证问卷结构完整性', shape='diamond', style='filled', fillcolor='lightyellow') 
dot.node('save_survey', '保存问卷数据', shape='box')
dot.node('update_index', '更新问卷索引', shape='box')
dot.node('error_url', 'URL格式错误', shape='box', style='filled', fillcolor='lightpink')
dot.node('error_fetch', '获取HTML失败', shape='box', style='filled', fillcolor='lightpink')
dot.node('error_parse', '解析问题失败', shape='box', style='filled', fillcolor='lightpink')
dot.node('error_structure', '问卷结构不完整', shape='box', style='filled', fillcolor='lightpink')
dot.node('end_success', '解析成功', shape='oval', style='filled', fillcolor='lightgreen')
dot.node('end_failure', '解析失败', shape='oval', style='filled', fillcolor='lightpink')

# 添加边
dot.edge('start', 'input_url')
dot.edge('input_url', 'validate_url')
dot.edge('validate_url', 'fetch_html', label='URL有效')
dot.edge('validate_url', 'error_url', label='URL无效')
dot.edge('fetch_html', 'check_fetch')
dot.edge('check_fetch', 'extract_meta', label='成功')
dot.edge('check_fetch', 'error_fetch', label='失败')
dot.edge('extract_meta', 'extract_questions')
dot.edge('extract_questions', 'process_questions')
dot.edge('process_questions', 'check_questions')
dot.edge('check_questions', 'extract_logic', label='完整')
dot.edge('check_questions', 'error_parse', label='不完整')
dot.edge('extract_logic', 'build_structure')
dot.edge('build_structure', 'validate_structure')
dot.edge('validate_structure', 'save_survey', label='有效')
dot.edge('validate_structure', 'error_structure', label='无效')
dot.edge('save_survey', 'update_index')
dot.edge('update_index', 'end_success')
dot.edge('error_url', 'end_failure')
dot.edge('error_fetch', 'end_failure')
dot.edge('error_parse', 'end_failure')
dot.edge('error_structure', 'end_failure')

# 保存图表
dot.render('survey_parsing_flow', directory='./output', cleanup=True)
print("图表已生成: ./output/survey_parsing_flow.png") 