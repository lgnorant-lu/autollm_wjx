import json
import os
import sys

def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print('问卷ID:', data['id'])
            print('问卷标题:', data['title'])
            print('问题数量:', len(data['questions']))
            print('\n第一题:')
            q1 = data['questions'][0]
            print(f"- 题目: {q1['title']}")
            print(f"- 类型: {q1['type']}")
            if q1.get('options'):
                print(f"- 选项: {q1['options']}")
            
            print('\n第二题:')
            q2 = data['questions'][1]
            print(f"- 题目: {q2['title']}")
            print(f"- 类型: {q2['type']}")
            if q2.get('options'):
                print(f"- 选项: {q2['options']}")
    except Exception as e:
        print(f"读取JSON文件出错: {e}")

if __name__ == "__main__":
    # 从data目录获取最新的问卷文件
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print(f"目录 {data_dir} 不存在")
        sys.exit(1)
        
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not json_files:
        print(f"未找到JSON文件在 {data_dir} 目录")
        sys.exit(1)
        
    # 按修改时间排序，取最新的
    latest_file = max(json_files, key=lambda f: os.path.getmtime(os.path.join(data_dir, f)))
    file_path = os.path.join(data_dir, latest_file)
    
    print(f"读取最新问卷文件: {file_path}\n")
    read_json_file(file_path)
