"""
----------------------------------------------------------------
File name:                  llm_zhipu_test.py
Author:                     Ignorant-lu
Date created:               2025/04/02
Description:                智谱AI LLM测试工具
----------------------------------------------------------------

Changed history:            
                            2025/04/02: 初始创建
----------------------------------------------------------------
"""

import sys
import json
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
from backend.utils.env_loader import EnvLoader

def main():
    """
    主函数
    """
    # 加载环境变量
    env_file = Path('.env.test')
    if env_file.exists():
        EnvLoader.load_env(str(env_file))
        logging.info(f"从文件加载环境变量: {env_file}")
    else:
        logging.warning(f"环境变量文件不存在: {env_file}")
    
    # 测试智谱AI提供商
    provider_name = 'zhipu'
    logging.info(f"测试提供商: {provider_name}")
    
    try:
        # 创建LLM生成器
        generator = LLMGenerator(
            model_type=provider_name,
            api_key=f"test-{provider_name}-api-key",
            mock=True  # 启用模拟模式
        )
        
        logging.info(f"成功创建LLM生成器: {provider_name}")
        logging.info(f"模拟模式: {generator.mock}")
        logging.info(f"提供商类型: {generator.provider.__class__.__name__}")
        
        # 测试文本生成
        prompt = "请用一句话介绍人工智能。"
        logging.info(f"提示词: {prompt}")
        
        logging.info("开始生成文本...")
        response = generator.provider.generate(prompt)
        logging.info(f"生成结果: {response}")
        
        # 测试JSON生成
        json_prompt = """请生成一个包含3个用户信息的JSON数据，每个用户包含以下字段：
- id: 用户ID（数字）
- name: 用户名（字符串）
- age: 年龄（数字）
- email: 邮箱（字符串）
"""
        logging.info(f"JSON提示词: {json_prompt}")
        
        logging.info("开始生成JSON...")
        json_response = generator.provider.generate_json(json_prompt)
        logging.info(f"生成结果: {json.dumps(json_response, ensure_ascii=False, indent=2)}")
        
        logging.info("测试成功")
    except Exception as e:
        logging.error(f"测试失败: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    main()
