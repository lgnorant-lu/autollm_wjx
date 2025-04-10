#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表名称: 实体关系图
创建日期: 2023-12-10
最后更新: 2023-12-10
描述: 展示问卷星自动化系统的主要数据实体及其关系
"""

import graphviz

# 创建图表
dot = graphviz.Digraph('Entity Relationship Diagram', 
                      comment='问卷星自动化系统实体关系图',
                      format='png')
dot.attr(rankdir='LR', size='8,10', dpi='300')

# 定义实体样式
entity_style = {
    'shape': 'box',
    'style': 'filled',
    'fillcolor': 'lightblue',
    'fontname': 'Arial',
    'margin': '0.3,0.1'
}

# 定义关系样式
edge_style = {
    'fontname': 'Arial',
    'fontsize': '10'
}

# 创建实体节点
dot.node('survey', '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>问卷 (Survey)</B></TD></TR>
            <TR><TD>survey_id</TD><TD>UUID</TD></TR>
            <TR><TD>title</TD><TD>String</TD></TR>
            <TR><TD>url</TD><TD>String</TD></TR>
            <TR><TD>created_at</TD><TD>DateTime</TD></TR>
            <TR><TD>updated_at</TD><TD>DateTime</TD></TR>
            <TR><TD>status</TD><TD>Enum</TD></TR>
            <TR><TD>metadata</TD><TD>JSON</TD></TR>
         </TABLE>>''', shape='none')

dot.node('question', '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>问题 (Question)</B></TD></TR>
            <TR><TD>question_id</TD><TD>UUID</TD></TR>
            <TR><TD>survey_id</TD><TD>UUID</TD></TR>
            <TR><TD>type</TD><TD>Enum</TD></TR>
            <TR><TD>title</TD><TD>String</TD></TR>
            <TR><TD>options</TD><TD>JSON</TD></TR>
            <TR><TD>required</TD><TD>Boolean</TD></TR>
            <TR><TD>order</TD><TD>Integer</TD></TR>
            <TR><TD>metadata</TD><TD>JSON</TD></TR>
         </TABLE>>''', shape='none')

dot.node('task', '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>任务 (Task)</B></TD></TR>
            <TR><TD>task_id</TD><TD>UUID</TD></TR>
            <TR><TD>survey_id</TD><TD>UUID</TD></TR>
            <TR><TD>created_at</TD><TD>DateTime</TD></TR>
            <TR><TD>updated_at</TD><TD>DateTime</TD></TR>
            <TR><TD>status</TD><TD>Enum</TD></TR>
            <TR><TD>count</TD><TD>Integer</TD></TR>
            <TR><TD>progress</TD><TD>Float</TD></TR>
            <TR><TD>settings</TD><TD>JSON</TD></TR>
         </TABLE>>''', shape='none')

dot.node('submission', '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>提交 (Submission)</B></TD></TR>
            <TR><TD>submission_id</TD><TD>UUID</TD></TR>
            <TR><TD>task_id</TD><TD>UUID</TD></TR>
            <TR><TD>survey_id</TD><TD>UUID</TD></TR>
            <TR><TD>created_at</TD><TD>DateTime</TD></TR>
            <TR><TD>status</TD><TD>Enum</TD></TR>
            <TR><TD>answers</TD><TD>JSON</TD></TR>
            <TR><TD>metadata</TD><TD>JSON</TD></TR>
         </TABLE>>''', shape='none')

dot.node('answer', '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>答案 (Answer)</B></TD></TR>
            <TR><TD>answer_id</TD><TD>UUID</TD></TR>
            <TR><TD>submission_id</TD><TD>UUID</TD></TR>
            <TR><TD>question_id</TD><TD>UUID</TD></TR>
            <TR><TD>value</TD><TD>JSON</TD></TR>
            <TR><TD>created_at</TD><TD>DateTime</TD></TR>
         </TABLE>>''', shape='none')

dot.node('config', '''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
            <TR><TD COLSPAN="2" BGCOLOR="lightblue"><B>配置 (Config)</B></TD></TR>
            <TR><TD>config_id</TD><TD>UUID</TD></TR>
            <TR><TD>name</TD><TD>String</TD></TR>
            <TR><TD>value</TD><TD>JSON</TD></TR>
            <TR><TD>updated_at</TD><TD>DateTime</TD></TR>
            <TR><TD>category</TD><TD>Enum</TD></TR>
         </TABLE>>''', shape='none')

# 添加关系
dot.edge('survey', 'question', label='1:n')
dot.edge('survey', 'task', label='1:n')
dot.edge('task', 'submission', label='1:n')
dot.edge('submission', 'answer', label='1:n')
dot.edge('question', 'answer', label='1:n')
dot.edge('config', 'task', label='n:m', style='dashed')
dot.edge('survey', 'submission', label='1:n', style='dashed')

# 保存图表
dot.render('entity_relationship', directory='./output', cleanup=True)
print("图表已生成: ./output/entity_relationship.png") 