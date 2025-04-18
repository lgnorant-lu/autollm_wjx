"""
----------------------------------------------------------------
File name:                  config_routes.py
Author:                     Ignorant-lu
Date created:               2025/02/17
Description:                配置API路由模块，提供系统配置的HTTP接口
----------------------------------------------------------------

Changed history:
                            2025/02/25: 增加代理和LLM配置管理
----------------------------------------------------------------
"""

from flask import Blueprint, request, jsonify
import json
import os

config_bp = Blueprint('config', __name__)

# 配置文件路径
from config import Config, APP_VERSION, APP_VERSION_INFO
CONFIG_FILE = os.path.join(Config.DATA_DIR, 'system_config.json')

def load_config():
    """
    加载系统配置

    从配置文件读取系统配置信息
    如果环境变量中有相关配置，优先使用环境变量中的配置

    Returns:
        dict: 系统配置信息
    """
    # 默认配置
    default_config = {
        "proxy_settings": {
            "enabled": False,
            "url": ""
        },
        "llm_settings": {
            "enabled": False,
            "provider": "aliyun",
            "api_key": ""
        }
    }

    # 从文件加载配置
    config = default_config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"读取配置文件失败: {e}")

    # 从环境变量加载代理配置
    pinzan_api_url = os.environ.get('PINZAN_API_URL')
    if pinzan_api_url:
        config['proxy_settings']['enabled'] = True
        config['proxy_settings']['url'] = pinzan_api_url

    # 从环境变量加载LLM配置
    # 首先检查默认的阿里云配置
    aliyun_api_key = os.environ.get('ALIYUN_API_KEY')
    if aliyun_api_key:
        config['llm_settings']['enabled'] = True
        config['llm_settings']['provider'] = 'aliyun'
        config['llm_settings']['api_key'] = aliyun_api_key

    # 检查其他LLM提供商的API密钥
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    zhipu_api_key = os.environ.get('ZHIPU_API_KEY')
    baidu_api_key = os.environ.get('BAIDU_API_KEY')
    gemini_api_key = os.environ.get('GEMINI_API_KEY')

    # 如果有其他API密钥但没有阿里云的，使用可用的其他提供商
    if not aliyun_api_key:
        if openai_api_key:
            config['llm_settings']['enabled'] = True
            config['llm_settings']['provider'] = 'openai'
            config['llm_settings']['api_key'] = openai_api_key
        elif zhipu_api_key:
            config['llm_settings']['enabled'] = True
            config['llm_settings']['provider'] = 'zhipu'
            config['llm_settings']['api_key'] = zhipu_api_key
        elif baidu_api_key:
            config['llm_settings']['enabled'] = True
            config['llm_settings']['provider'] = 'baidu'
            config['llm_settings']['api_key'] = baidu_api_key
        elif gemini_api_key:
            config['llm_settings']['enabled'] = True
            config['llm_settings']['provider'] = 'gemini'
            config['llm_settings']['api_key'] = gemini_api_key

    return config

def save_config(config):
    """
    保存系统配置

    将系统配置信息写入配置文件并更新环境变量

    Args:
        config (dict): 系统配置信息
    """
    # 保存到文件
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    # 更新环境变量
    # 代理设置
    if config.get('proxy_settings', {}).get('enabled', False) and config.get('proxy_settings', {}).get('url'):
        os.environ['PINZAN_API_URL'] = config['proxy_settings']['url']

    # LLM设置
    if config.get('llm_settings', {}).get('enabled', False):
        provider = config['llm_settings'].get('provider', 'aliyun')
        api_key = config['llm_settings'].get('api_key', '')
        if api_key:
            os.environ[f"{provider.upper()}_API_KEY"] = api_key

@config_bp.route('', methods=['GET'])
def get_config():
    """
    获取系统配置

    返回系统配置信息

    Returns:
        dict: 系统配置信息
    """
    config = load_config()
    # 隐藏敏感信息
    if 'llm_settings' in config and 'api_key' in config['llm_settings']:
        key = config['llm_settings']['api_key']
        if key:
            config['llm_settings']['api_key'] = '**********'
    return jsonify(config)

@config_bp.route('/version', methods=['GET'])
def get_version():
    """
    获取应用版本信息

    Returns:
        dict: 应用版本信息
    """
    # 返回完整的版本信息
    return jsonify(APP_VERSION_INFO)

@config_bp.route('', methods=['PUT'])
def update_config():
    """
    更新系统配置

    更新系统配置信息

    Args:
        data (dict): 新的系统配置信息

    Returns:
        dict: 更新结果
    """
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    current_config = load_config()

    # 更新代理设置
    if 'proxy_settings' in data:
        current_config['proxy_settings'] = data['proxy_settings']

    # 更新LLM设置
    if 'llm_settings' in data:
        # 如果API密钥是掩码，则保留原值
        if data['llm_settings'].get('api_key') == '**********':
            data['llm_settings']['api_key'] = current_config['llm_settings'].get('api_key', '')
        current_config['llm_settings'] = data['llm_settings']

    save_config(current_config)
    return jsonify({"success": True})