"""
----------------------------------------------------------------
File name:                  llm_with_proxy_example.py
Author:                     Ignorant-lu
Date created:               2025/04/02
Description:                LLM API和IP代理使用示例
----------------------------------------------------------------

Changed history:            
                            2025/04/02: 初始创建
----------------------------------------------------------------
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.append(str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入相关模块
from backend.core.llm_generator import LLMGenerator
from backend.utils.proxy.manager import ProxyManager
from backend.utils.env_loader import EnvLoader

def main():
    """
    主函数
    """
    # 加载环境变量
    env_file = Path(__file__).parent.parent / '.env'
    EnvLoader.load_env(str(env_file))
    
    # 创建代理管理器
    proxy_config = Path(__file__).parent.parent / 'config' / 'proxy_config.json'
    proxy_manager = ProxyManager(config_file=str(proxy_config))
    
    # 获取代理
    proxy = proxy_manager.get_proxy()
    if proxy:
        logging.info(f"获取到代理: {proxy}")
        
        # 验证代理
        is_valid = proxy_manager.validate_proxy(proxy)
        logging.info(f"代理有效性: {is_valid}")
        
        # 获取当前IP
        current_ip = proxy_manager.get_current_ip(proxy)
        logging.info(f"当前IP: {current_ip}")
    else:
        logging.warning("未获取到代理，将使用直连")
    
    # 获取可用的LLM提供商
    providers = LLMGenerator.get_available_providers()
    logging.info(f"可用的LLM提供商: {providers}")
    
    # 创建LLM生成器
    llm_generator = LLMGenerator(
        model_type="openai",  # 可以根据需要更改为其他提供商
        model_name="gpt-3.5-turbo",  # 可以根据需要更改为其他模型
        proxy=proxy  # 设置代理
    )
    
    # 测试生成
    prompt = "请用一句话介绍人工智能。"
    logging.info(f"测试生成，提示词: {prompt}")
    
    try:
        response = llm_generator.generate(prompt)
        logging.info(f"生成结果: {response}")
    except Exception as e:
        logging.error(f"生成失败: {str(e)}")
    
    # 测试问卷答案生成
    question_data = {
        "question": "你平时喜欢什么运动？",
        "options": ["跑步", "游泳", "篮球", "足球", "其他"],
        "type": "single_choice"
    }
    
    logging.info(f"测试问卷答案生成，问题: {question_data['question']}")
    
    try:
        answer = llm_generator.generate_answer(question_data)
        logging.info(f"生成答案: {answer}")
    except Exception as e:
        logging.error(f"生成答案失败: {str(e)}")

if __name__ == "__main__":
    main()
