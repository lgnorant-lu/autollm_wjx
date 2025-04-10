#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本名称: 图表批量生成脚本
创建日期: 2024-03-28
描述: 批量生成所有图表的脚本
"""

import os
import subprocess
import time
import glob

def create_output_dirs():
    """创建输出目录"""
    output_dir = './docs/diagrams/output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 为各类型图表创建子目录
    for subdir in ['Architecture', 'Modules', 'Flowcharts', 'Algorithms', 'DataModels', 'UI']:
        if not os.path.exists(f'{output_dir}/{subdir}'):
            os.makedirs(f'{output_dir}/{subdir}')

def generate_diagrams():
    """执行所有图表生成脚本"""
    # 获取所有Python图表脚本
    diagram_scripts = []
    diagram_dirs = [
        './docs/diagrams/Architecture',
        './docs/diagrams/Modules',
        './docs/diagrams/Flowcharts',
        './docs/diagrams/Algorithms',
        './docs/diagrams/DataModels',
    ]
    
    for dir_path in diagram_dirs:
        if os.path.exists(dir_path):
            scripts = glob.glob(f'{dir_path}/*.py')
            diagram_scripts.extend(scripts)
    
    # 计数器
    total = len(diagram_scripts)
    successful = 0
    failed = 0
    
    print(f"开始生成 {total} 个图表...")
    
    # 执行每个脚本
    for script in diagram_scripts:
        script_name = os.path.basename(script)
        print(f"正在生成: {script_name}")
        try:
            # 使用Python执行脚本
            result = subprocess.run(['python', script], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True)
            
            if result.returncode == 0:
                print(f"✓ 成功: {script_name}")
                successful += 1
            else:
                print(f"✗ 失败: {script_name}")
                print(f"  错误: {result.stderr}")
                failed += 1
                
        except Exception as e:
            print(f"✗ 失败: {script_name}")
            print(f"  异常: {str(e)}")
            failed += 1
            
        # 短暂暂停，避免资源竞争
        time.sleep(0.2)
    
    # 输出结果统计
    print("\n图表生成完成!")
    print(f"总计: {total} 个图表")
    print(f"成功: {successful} 个")
    print(f"失败: {failed} 个")
    
    return successful, failed, total

if __name__ == "__main__":
    print("=== 问卷星自动化系统图表生成工具 ===")
    
    # 创建输出目录
    create_output_dirs()
    
    # 记录开始时间
    start_time = time.time()
    
    # 生成图表
    successful, failed, total = generate_diagrams()
    
    # 计算执行时间
    elapsed_time = time.time() - start_time
    
    print(f"\n总执行时间: {elapsed_time:.2f} 秒")
    
    # 返回状态码
    if failed > 0:
        exit(1)
    else:
        exit(0) 