"""AI相关路由"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from src.app import db
from src.app.models_extended import User, UserRole, AIAnalysis, Task
from src.app.ai_integration import task_analyzer, task_allocator, AIModelType
import os

ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

@ai_bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze_task():
    """AI任务分析页面"""
    if current_user.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
        flash('只有经理和总监可以使用AI分析功能', 'warning')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        user_input = request.form.get('task_input', '').strip()
        
        if not user_input:
            flash('请输入任务描述', 'danger')
            return render_template('ai/analyze.html')
        
        if len(user_input) < 10:
            flash('请输入更详细的任务描述（至少10个字符）', 'warning')
            return render_template('ai/analyze.html')
        
        # 根据配置选择AI模型
        model_type = os.environ.get('AI_MODEL_TYPE', 'mock').lower()
        if model_type == 'deepseek':
            task_analyzer.model_type = AIModelType.DEEPSEEK
        elif model_type == 'openai':
            task_analyzer.model_type = AIModelType.OPENAI
        elif model_type == 'local':
            task_analyzer.model_type = AIModelType.LOCAL
        else:
            task_analyzer.model_type = AIModelType.MOCK
        
        # 分析任务
        try:
            analysis_result = task_analyzer.analyze_task(user_input, current_user.id)
            
            # 保存分析结果
            analysis = task_analyzer.save_analysis(user_input, current_user.id, analysis_result)
            
            # 创建实际任务
            created_tasks = []
            if 'tasks' in analysis_result:
                for task_data in analysis_result['tasks']:
                    # 查找分配的用户
                    assigned_user = None
                    if task_data.get('assigned_to'):
                        assigned_user = User.query.filter_by(username=task_data['assigned_to']).first()
                    
                    # 创建任务
                    task = Task(
                        title=task_data['title'],
                        description=task_data['description'],
                        status='ASSIGNED' if assigned_user else 'PENDING',
                        priority=task_data['priority'],
                        estimated_hours=task_data['estimated_hours'],
                        assigned_to_id=assigned_user.id if assigned_user else None,
                        created_by_id=current_user.id,
                        ai_analysis_id=analysis.id
                    )
                    
                    # 设置截止日期
                    if task_data.get('due_date'):
                        task.due_date = datetime.fromisoformat(task_data['due_date'])
                    
                    db.session.add(task)
                    created_tasks.append(task)
                
                db.session.commit()
            
            flash(f'AI分析完成！已创建{len(created_tasks)}个任务。', 'success')
            return redirect(url_for('ai.analysis_result', analysis_id=analysis.id))
            
        except Exception as e:
            flash(f'分析失败: {str(e)}', 'danger')
            return render_template('ai/analyze.html')
    
    return render_template('ai/analyze.html')

@ai_bp.route('/analysis/<int:analysis_id>')
@login_required
def analysis_result(analysis_id):
    """查看分析结果"""
    analysis = AIAnalysis.query.get_or_404(analysis_id)
    
    # 检查权限
    if analysis.input_by_id != current_user.id and current_user.role != UserRole.DIRECTOR:
        flash('无权查看此分析结果', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # 获取步骤
    steps = analysis.get_steps()
    
    # 获取下属员工（用于分配）
    employees = []
    if current_user.role == UserRole.MANAGER:
        employees = User.query.filter_by(
            reports_to_id=current_user.id,
            role=UserRole.EMPLOYEE,
            active=True
        ).all()
    elif current_user.role == UserRole.DIRECTOR:
        # 总监可以查看所有经理的员工
        managers = User.query.filter_by(
            reports_to_id=current_user.id,
            role=UserRole.MANAGER,
            active=True
        ).all()
        for manager in managers:
            manager_employees = User.query.filter_by(
                reports_to_id=manager.id,
                role=UserRole.EMPLOYEE,
                active=True
            ).all()
            employees.extend(manager_employees)
    
    return render_template('ai/analysis_result.html',
                         analysis=analysis,
                         steps=steps,
                         employees=employees,
                         step_count=len(steps))

@ai_bp.route('/allocate/<int:analysis_id>', methods=['POST'])
@login_required
def allocate_tasks(analysis_id):
    """分配任务给员工"""
    analysis = AIAnalysis.query.get_or_404(analysis_id)
    
    # 检查权限
    if analysis.input_by_id != current_user.id and current_user.role != UserRole.DIRECTOR:
        return jsonify({"success": False, "error": "无权分配此任务"}), 403
    
    if current_user.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
        return jsonify({"success": False, "error": "只有经理和总监可以分配任务"}), 403
    
    try:
        # 执行分配
        allocation_result = task_allocator.allocate_tasks(analysis_id, current_user.id)
        
        # 为每个分配的任务安排提醒
        for detail in allocation_result.get('details', []):
            task = Task.query.get(detail['task_id'])
            if task:
                from src.app.ai_integration import reminder_scheduler
                reminder_scheduler.schedule_task_reminders(task)
        
        return jsonify(allocation_result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@ai_bp.route('/history')
@login_required
def analysis_history():
    """查看分析历史"""
    if current_user.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
        flash('只有经理和总监可以查看分析历史', 'warning')
        return redirect(url_for('main.dashboard'))
    
    # 获取用户的AI分析历史
    analyses = AIAnalysis.query.filter_by(input_by_id=current_user.id)\
        .order_by(AIAnalysis.created_at.desc())\
        .all()
    
    # 获取每个分析对应的任务数量
    for analysis in analyses:
        analysis.task_count = Task.query.filter_by(ai_analysis_id=analysis.id).count()
    
    return render_template('ai/history.html', analyses=analyses)

@ai_bp.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    """API接口：AI任务分析"""
    if current_user.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
        return jsonify({"success": False, "error": "权限不足"}), 403
    
    data = request.get_json()
    if not data or 'input' not in data:
        return jsonify({"success": False, "error": "缺少输入参数"}), 400
    
    user_input = data['input'].strip()
    if len(user_input) < 10:
        return jsonify({"success": False, "error": "输入太短，请提供更详细的描述"}), 400
    
    # 根据配置选择AI模型
    model_type = os.environ.get('AI_MODEL_TYPE', 'mock').lower()
    if model_type == 'deepseek':
        task_analyzer.model_type = AIModelType.DEEPSEEK
    elif model_type == 'openai':
        task_analyzer.model_type = AIModelType.OPENAI
    elif model_type == 'local':
        task_analyzer.model_type = AIModelType.LOCAL
    else:
        task_analyzer.model_type = AIModelType.MOCK
    
    try:
        # 分析任务
        analysis_result = task_analyzer.analyze_task(user_input, current_user.id)
        
        # 保存分析结果
        analysis = task_analyzer.save_analysis(user_input, current_user.id, analysis_result)
        
        return jsonify({
            "success": True,
            "analysis_id": analysis.id,
            "result": analysis_result,
            "message": "分析完成"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@ai_bp.route('/api/allocate', methods=['POST'])
@login_required
def api_allocate():
    """API接口：分配任务"""
    if current_user.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
        return jsonify({"success": False, "error": "权限不足"}), 403
    
    data = request.get_json()
    if not data or 'analysis_id' not in data:
        return jsonify({"success": False, "error": "缺少分析ID"}), 400
    
    analysis_id = data['analysis_id']
    
    try:
        # 执行分配
        allocation_result = task_allocator.allocate_tasks(analysis_id, current_user.id)
        
        # 为每个分配的任务安排提醒
        for detail in allocation_result.get('details', []):
            task = Task.query.get(detail['task_id'])
            if task:
                from src.app.ai_integration import reminder_scheduler
                reminder_scheduler.schedule_task_reminders(task)
        
        return jsonify(allocation_result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500