"""
----------------------------------------------------------------
File name:                  llm_real_test.py
Author:                     Ignorant-lu
Date created:               2025/04/02
Description:                LLM真实API测试工具
----------------------------------------------------------------

Changed history:            
                            2025/04/02: 初始创建
----------------------------------------------------------------
"""

import os
import sys
import json
import logging
import argparse
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
from backend.utils.proxy.manager import ProxyManager

def setup_argparse():
    """
    设置命令行参数
    
    Returns:
        argparse.ArgumentParser: 命令行参数解析器
    """
    parser = argparse.ArgumentParser(description='LLM真实API测试工具')
    
    # 提供商类型
    parser.add_argument('--provider', '-p', type=str, default='openai',
                        help='LLM提供商类型: openai, zhipu, baidu, aliyun, tuzi, gemini')
    
    # 模型名称
    parser.add_argument('--model', '-m', type=str, default=None,
                        help='模型名称，如果不指定则使用默认模型')
    
    # 测试类型
    parser.add_argument('--test-type', '-t', type=str, default='text',
                        choices=['text', 'json', 'all'],
                        help='测试类型: text, json, all')
    
    # 提示词
    parser.add_argument('--prompt', type=str, default=None,
                        help='测试提示词，如果不指定则使用默认提示词')
    
    # 详细模式
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='详细模式')
    
    # 环境变量文件
    parser.add_argument('--env-file', type=str, default='.env.real',
                        help='环境变量文件路径')
    
    # API密钥
    parser.add_argument('--api-key', type=str, default=None,
                        help='API密钥，如果不指定则从环境变量中获取')
    
    # 温度
    parser.add_argument('--temperature', type=float, default=0.7,
                        help='生成温度，值越高结果越随机')
    
    # 最大令牌数
    parser.add_argument('--max-tokens', type=int, default=500,
                        help='最大生成令牌数')
    
    # 使用代理
    parser.add_argument('--use-proxy', action='store_true',
                        help='是否使用代理')
    
    return parser

def test_text_generation(generator, prompt=None):
    """
    测试文本生成
    
    Args:
        generator: LLM生成器
        prompt: 提示词，如果为None则使用默认提示词
    """
    logging.info("=== 测试文本生成 ===")
    
    # 使用默认提示词
    if prompt is None:
        prompt = "请用一句话介绍人工智能。"
    
    logging.info(f"提示词: {prompt}")
    
    try:
        logging.info(f"提供商类型: {generator.provider.__class__.__name__}")
        logging.info(f"模型: {generator.provider.model}")
        
        # 生成文本
        logging.info("开始生成文本...")
        response = generator.provider.generate(prompt)
        logging.info(f"生成结果: {response}")
        return True
    except Exception as e:
        logging.error(f"生成失败: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return False

def test_json_generation(generator, prompt=None):
    """
    测试JSON生成
    
    Args:
        generator: LLM生成器
        prompt: 提示词，如果为None则使用默认提示词
    """
    logging.info("=== 测试JSON生成 ===")
    
    # 使用默认提示词
    if prompt is None:
        prompt = """请生成一个包含3个用户信息的JSON数据，每个用户包含以下字段：
- id: 用户ID（数字）
- name: 用户名（字符串）
- age: 年龄（数字）
- email: 邮箱（字符串）
"""
    
    logging.info(f"提示词: {prompt}")
    
    try:
        logging.info(f"提供商类型: {generator.provider.__class__.__name__}")
        logging.info(f"模型: {generator.provider.model}")
        
        # 生成JSON
        logging.info("开始生成JSON...")
        response = generator.provider.generate_json(prompt)
        logging.info(f"生成结果: {json.dumps(response, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        logging.error(f"生成失败: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return False

def main():
    """
    主函数
    """
    # 解析命令行参数
    parser = setup_argparse()
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 加载环境变量
    env_file = Path(args.env_file)
    if env_file.exists():
        EnvLoader.load_env(str(env_file))
        logging.info(f"从文件加载环境变量: {env_file}")
    else:
        logging.warning(f"环境变量文件不存在: {env_file}")
    
    # 获取可用的LLM提供商
    providers = LLMGenerator.get_available_providers()
    logging.info(f"可用的LLM提供商: {list(providers.keys())}")
    
    # 检查提供商是否可用
    if args.provider not in providers:
        logging.error(f"未知的LLM提供商: {args.provider}")
        return
    
    # 设置代理
    proxy = None
    if args.use_proxy:
        try:
            # 创建代理管理器
            proxy_manager = ProxyManager(
                config_file="config/proxy_config.json",
                env_file=args.env_file
            )
            
            # 获取代理
            proxy = proxy_manager.get_proxy()
            if proxy:
                logging.info(f"使用代理: {proxy}")
            else:
                logging.warning("无法获取代理，将直接连接")
        except Exception as e:
            logging.error(f"获取代理失败: {str(e)}")
            logging.warning("将直接连接")
    
    try:
        # 创建LLM生成器
        generator = LLMGenerator(
            model_type=args.provider,
            api_key=args.api_key,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            proxy=proxy
        )
        
        logging.info(f"成功创建LLM生成器: {args.provider}")
        
        # 运行测试
        results = {}
        
        if args.test_type in ['text', 'all']:
            results['text'] = test_text_generation(generator, args.prompt)
        
        if args.test_type in ['json', 'all']:
            results['json'] = test_json_generation(generator, args.prompt)
        
        # 输出测试结果
        logging.info("=== 测试结果 ===")
        for test_type, success in results.items():
            logging.info(f"{test_type}: {'成功' if success else '失败'}")
        
        # 总结
        if all(results.values()):
            logging.info("所有测试都成功")
        elif any(results.values()):
            logging.info("部分测试成功")
        else:
            logging.error("所有测试都失败")
            
    except Exception as e:
        logging.error(f"测试过程中发生错误: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    main()
