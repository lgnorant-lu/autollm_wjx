import json
import os

def optimize_question_data(input_path, output_path):
    """
    优化问卷数据结构，减少冗余
    
    Args:
        input_path: 原始JSON路径
        output_path: 优化后的JSON路径
    """
    # 读取原始数据
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建优化后的数据结构
    optimized_data = {
        "id": data.get("id", ""),
        "title": data.get("title", ""),
        "questions": []
    }
    
    # 遍历每个问题，只保留必要字段
    for q in data["questions"]:
        opt_q = {
            "idx": q["index"],
            "type": q["type"],
            "title": q.get("title", "").strip(),
        }
        
        # 根据题型保留不同字段
        if q["type"] == 1:  # 填空题
            opt_q["format"] = "text"
            
        elif q["type"] == 3:  # 单选题
            opt_q["format"] = "single"
            opt_q["options"] = [o.strip() if isinstance(o, str) else o.get("text", "").strip() for o in q.get("options", [])]
            
        elif q["type"] == 4:  # 多选题
            opt_q["format"] = "multiple"
            opt_q["options"] = [o.strip() if isinstance(o, str) else o.get("text", "").strip() for o in q.get("options", [])]
            
        elif q["type"] == 2:  # 矩阵题
            opt_q["format"] = "matrix"
            opt_q["rows"] = [r.get("text", "").strip() for r in q.get("matrix_rows", [])]
            opt_q["columns"] = [c.get("text", "").strip() for c in q.get("matrix_options", [])]
        
        # 忽略隐藏题目
        if not q.get("is_hidden", False):
            optimized_data["questions"].append(opt_q)
    
    # 写入优化后的数据
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(optimized_data, f, ensure_ascii=False, indent=2)
    
    return optimized_data 