"""
----------------------------------------------------------------
File name:                  task_routes.py
Author:                     Ignorant-lu
Date created:               2025/02/17
Description:                任务相关路由模块，提供任务创建、管理和操作的API接口
----------------------------------------------------------------

Changed history:            
                            2025/02/18: 增加任务状态控制API接口
                            2025/02/22: 增加任务分页和排序功能
                            2025/02/23: 完善错误处理和日志记录
----------------------------------------------------------------
"""

from flask import Blueprint, request, jsonify
from services.task_service import TaskService
import logging
import traceback

logger = logging.getLogger(__name__)

task_bp = Blueprint('task', __name__)
task_service = TaskService()

@task_bp.route('', methods=['POST'])
def create_task():
    """
    创建新任务API
    
    接收任务参数，创建新的问卷提交任务
    
    Returns:
        JSON: 创建结果，包含任务ID和基本信息
    """
    """创建新任务"""
    data = request.json
    required_fields = ['survey_id', 'count']
    
    logger.info(f"收到创建任务请求: {data}")
    
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        task_id = task_service.create_task(data)
        return jsonify({"task_id": task_id})
    except Exception as e:
        logger.error(f"创建任务失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@task_bp.route('', methods=['GET'])
def get_tasks():
    """
    获取所有任务API
    
    支持分页和排序，返回任务列表
    
    Returns:
        JSON: 任务列表，包含任务基本信息和分页信息
    """
    """获取所有任务，支持分页和排序"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    sort_field = request.args.get('sort_field', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # 验证并限制分页参数
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10
    
    # 验证排序字段和顺序
    valid_sort_fields = ['id', 'survey_id', 'status', 'progress', 'count', 'created_at', 'updated_at']
    if sort_field not in valid_sort_fields:
        sort_field = 'created_at'
    
    valid_sort_orders = ['asc', 'desc']
    if sort_order not in valid_sort_orders:
        sort_order = 'desc'
    
    # 获取任务列表
    tasks, total = task_service.get_tasks_paginated(
        page=page,
        page_size=page_size,
        sort_field=sort_field,
        sort_order=sort_order
    )
    
    return jsonify({
        "items": tasks,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size  # 计算总页数
    })

@task_bp.route('/<task_id>', methods=['GET'])
def get_task(task_id):
    """
    获取任务详情API
    
    根据任务ID获取任务详细信息
    
    Returns:
        JSON: 任务详细信息
    """
    """获取任务详情"""
    task = task_service.get_task_by_id(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"data": task})

@task_bp.route('/<task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    """
    更新任务状态API
    
    根据任务ID更新任务状态
    
    Returns:
        JSON: 更新结果
    """
    """更新任务状态"""
    data = request.json
    if not data or 'status' not in data:
        return jsonify({"error": "Missing status parameter"}), 400
    
    status = data['status']
    if status not in ['running', 'paused', 'stopped']:
        return jsonify({"error": "Invalid status value"}), 400
    
    success = task_service.update_task_status(task_id, status)
    if not success:
        return jsonify({"error": "Failed to update task status"}), 500
    return jsonify({"success": True})

@task_bp.route('/<task_id>/pause', methods=['POST'])
def pause_task(task_id):
    """
    暂停任务API
    
    根据任务ID暂停任务
    
    Returns:
        JSON: 暂停结果
    """
    """暂停任务"""
    try:
        logger.info(f"尝试暂停任务: {task_id}")
        success = task_service.update_task_status(task_id, 'paused')
        if not success:
            logger.error(f"暂停任务失败: {task_id}, 任务可能不存在或状态不允许暂停")
            return jsonify({"error": "Failed to pause task, it may not exist or be in a state that cannot be paused"}), 400
        logger.info(f"成功暂停任务: {task_id}")
        return jsonify({"success": True, "message": "Task paused successfully"})
    except Exception as e:
        logger.exception(f"暂停任务时发生异常: {task_id}, {str(e)}")
        return jsonify({"error": f"Exception occurred: {str(e)}"}), 500

@task_bp.route('/<task_id>/resume', methods=['POST'])
def resume_task(task_id):
    """
    恢复任务API
    
    根据任务ID恢复任务
    
    Returns:
        JSON: 恢复结果
    """
    """恢复任务"""
    try:
        logger.info(f"尝试恢复任务: {task_id}")
        success = task_service.update_task_status(task_id, 'running')
        if not success:
            logger.error(f"恢复任务失败: {task_id}, 任务可能不存在或状态不允许恢复")
            return jsonify({"error": "Failed to resume task, it may not exist or be in a state that cannot be resumed"}), 400
        logger.info(f"成功恢复任务: {task_id}")
        return jsonify({"success": True, "message": "Task resumed successfully"})
    except Exception as e:
        logger.exception(f"恢复任务时发生异常: {task_id}, {str(e)}")
        return jsonify({"error": f"Exception occurred: {str(e)}"}), 500

@task_bp.route('/<task_id>/stop', methods=['POST'])
def stop_task(task_id):
    """
    停止任务API
    
    根据任务ID停止任务
    
    Returns:
        JSON: 停止结果
    """
    """停止任务"""
    try:
        logger.info(f"尝试停止任务: {task_id}")
        success = task_service.update_task_status(task_id, 'stopped')
        if not success:
            logger.error(f"停止任务失败: {task_id}, 任务可能不存在或状态不允许停止")
            return jsonify({"error": "Failed to stop task, it may not exist or be in a state that cannot be stopped"}), 400
        logger.info(f"成功停止任务: {task_id}")
        return jsonify({"success": True, "message": "Task stopped successfully"})
    except Exception as e:
        logger.exception(f"停止任务时发生异常: {task_id}, {str(e)}")
        return jsonify({"error": f"Exception occurred: {str(e)}"}), 500

@task_bp.route('/<task_id>/refresh', methods=['POST'])
def refresh_task(task_id):
    """
    刷新任务状态API
    
    根据任务ID刷新任务状态和进度信息
    
    Returns:
        JSON: 刷新结果
    """
    """刷新任务状态和进度信息"""
    try:
        logger.info(f"刷新任务状态: {task_id}")
        task = task_service.get_task_by_id(task_id)
        
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        # 计算处理进度，如果有success_count和count数据
        if 'success_count' in task and 'count' in task and task['count'] > 0:
            task['progress'] = min(round((task['success_count'] / task['count']) * 100), 100)
        
        # 如果已完成所有任务但状态未更新，将状态设为完成
        total_processed = (task.get('success_count', 0) + task.get('fail_count', 0))
        if total_processed >= task.get('count', 0) and task['status'] == 'running':
            task_service.update_task_status(task_id, 'completed')
            task['status'] = 'completed'
            task['progress'] = 100
            
        return jsonify({"success": True, "data": task})
    except Exception as e:
        logger.exception(f"刷新任务状态时发生异常: {task_id}, {str(e)}")
        return jsonify({"error": f"Exception occurred: {str(e)}"}), 500

@task_bp.route('/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    删除任务API
    
    根据任务ID删除任务
    
    Returns:
        JSON: 删除结果
    """
    """删除任务"""
    success = task_service.delete_task(task_id)
    if not success:
        return jsonify({"error": "Failed to delete task"}), 500
    return jsonify({"success": True}) 