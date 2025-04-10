"""
----------------------------------------------------------------
File name:                  survey_routes.py
Author:                     Ignorant-lu
Date created:               2025/02/17
Description:                问卷相关路由模块，提供问卷解析和管理的API接口
----------------------------------------------------------------

Changed history:            
                            2025/02/18: 增加详细的错误处理和日志记录
                            2025/02/23: 优化API响应格式
----------------------------------------------------------------
"""

from flask import Blueprint, request, jsonify
from services.survey_service import SurveyService
import logging

logger = logging.getLogger(__name__)

survey_bp = Blueprint('survey', __name__)
survey_service = SurveyService()

@survey_bp.route('/parse', methods=['POST'])
def parse_survey():
    """
    解析问卷API
    
    接收问卷URL，解析问卷结构并保存
    
    Returns:
        JSON: 解析结果，包含问卷ID和基本信息
    """
    """解析问卷"""
    try:
        logger.info("请求解析问卷")
        data = request.get_json()
        if not data or 'url' not in data:
            logger.error("请求缺少URL参数")
            return jsonify({"error": "请提供问卷URL", "code": 400, "message": "缺少URL参数"}), 400
        
        url = data['url']
        logger.info(f"接收到解析问卷请求: {url}")
        
        # 解析问卷
        try:
            survey = survey_service.parse_survey(url)
            logger.info(f"成功解析问卷: {survey['id']}")
            return jsonify({"data": survey, "code": 200, "message": "问卷解析成功"})
        except Exception as e:
            logger.error(f"解析问卷失败: {e}", exc_info=True)
            return jsonify({"error": str(e), "code": 500, "message": "问卷解析失败"}), 500
    except Exception as e:
        logger.error(f"处理问卷解析请求失败: {e}", exc_info=True)
        return jsonify({"error": str(e), "code": 500, "message": "处理请求失败"}), 500

@survey_bp.route('', methods=['GET'])
def get_all_surveys():
    """
    获取所有问卷API
    
    返回所有已保存的问卷列表
    
    Returns:
        JSON: 问卷列表
    """
    """获取所有问卷"""
    try:
        logger.info("请求获取所有问卷")
        surveys = survey_service.get_all_surveys()
        logger.info(f"成功获取到 {len(surveys)} 个问卷")
        return jsonify({"data": surveys, "code": 200, "message": "success"})
    except Exception as e:
        logger.error(f"获取问卷列表失败: {e}", exc_info=True)
        return jsonify({"error": str(e), "code": 500, "message": "获取问卷列表失败"}), 500

@survey_bp.route('/<survey_id>', methods=['GET'])
def get_survey(survey_id):
    """
    获取指定问卷详情API
    
    根据问卷ID返回问卷详情
    
    Args:
        survey_id (str): 问卷ID
    
    Returns:
        JSON: 问卷详情
    """
    """获取指定问卷详情"""
    try:
        logger.info(f"请求获取问卷 {survey_id} 详情")
        survey = survey_service.get_survey_by_id(survey_id)
        if not survey:
            logger.error(f"问卷 {survey_id} 不存在")
            return jsonify({"error": "Survey not found", "code": 404, "message": "问卷不存在"}), 404
        logger.info(f"成功获取到问卷 {survey_id} 详情")
        return jsonify({"data": survey, "code": 200, "message": "success"})
    except Exception as e:
        logger.error(f"获取问卷 {survey_id} 详情失败: {e}", exc_info=True)
        return jsonify({"error": str(e), "code": 500, "message": "获取问卷详情失败"}), 500

@survey_bp.route('/<survey_id>', methods=['DELETE'])
def delete_survey(survey_id):
    """
    删除问卷API
    
    根据问卷ID删除问卷
    
    Args:
        survey_id (str): 问卷ID
    
    Returns:
        JSON: 删除结果
    """
    """删除问卷"""
    try:
        logger.info(f"请求删除问卷 {survey_id}")
        success = survey_service.delete_survey(survey_id)
        if not success:
            logger.error(f"删除问卷 {survey_id} 失败")
            return jsonify({"error": "Failed to delete survey", "code": 500, "message": "删除问卷失败"}), 500
        logger.info(f"成功删除问卷 {survey_id}")
        return jsonify({"data": {"success": True}, "code": 200, "message": "success"})
    except Exception as e:
        logger.error(f"删除问卷 {survey_id} 失败: {e}", exc_info=True)
        return jsonify({"error": str(e), "code": 500, "message": "删除问卷失败"}), 500