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
from config import Config
CONFIG_FILE = os.path.join(Config.DATA_DIR, 'system_config.json')

def load_config():
    """
    加载系统配置

    从配置文件读取系统配置信息

    Returns:
        dict: 系统配置信息
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "proxy_settings": {
            "enabled": False,
            "url": ""
        },
        "llm_settings": {
            "enabled": False,
            "provider": "zhipu",
            "api_key": ""
        }
    }

def save_config(config):
    """
    保存系统配置

    将系统配置信息写入配置文件

    Args:
        config (dict): 系统配置信息
    """
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

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