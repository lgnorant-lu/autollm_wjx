"""
----------------------------------------------------------------
File name:                  llm_mock_test.py
Author:                     Ignorant-lu
Date created:               2025/04/02
Description:                LLM模拟测试工具
----------------------------------------------------------------

Changed history:            
                            2025/04/02: 初始创建
----------------------------------------------------------------
"""

import os
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
    
    # 获取可用的LLM提供商
    providers = LLMGenerator.get_available_providers()
    logging.info(f"可用的LLM提供商: {list(providers.keys())}")
    
    # 模拟测试每个提供商
    for provider_name in providers.keys():
        logging.info(f"测试提供商: {provider_name}")
        
        try:
            # 创建LLM提供商实例
            provider = LLMGenerator.create_provider(
                provider_name=provider_name,
                api_key=f"test-{provider_name}-api-key",
                mock=True  # 启用模拟模式
            )
            
            if provider:
                logging.info(f"成功创建提供商实例: {provider_name}")
                
                # 获取提供商的配置信息
                config = {
                    "api_base": getattr(provider, "api_base", None),
                    "model": getattr(provider, "model", None),
                    "timeout": getattr(provider, "timeout", None),
                    "temperature": getattr(provider, "temperature", None),
                    "max_tokens": getattr(provider, "max_tokens", None)
                }
                
                logging.info(f"提供商配置: {json.dumps(config, indent=2)}")
            else:
                logging.error(f"创建提供商实例失败: {provider_name}")
        except Exception as e:
            logging.error(f"测试提供商时发生错误: {provider_name}, 错误: {str(e)}")
    
    logging.info("模拟测试完成")

if __name__ == "__main__":
    main()
