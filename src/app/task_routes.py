"""任务视图相关路由"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from src.app import db
from src.app.models_extended import User, UserRole, Task, TaskStatus, TaskPriority
from src.app.task_views import task_view_generator, TimeView
from datetime import datetime, timedelta

task_bp = Blueprint('task', __name__, url_prefix='/tasks')

@task_bp.route('/')
@login_required
def list_tasks():
    """任务列表页面（根据用户角色显示不同视图）"""
    if current_user.role == UserRole.EMPLOYEE:
        return redirect(url_for('task.employee_view'))
    elif current_user.role == UserRole.MANAGER:
        return redirect(url_for('task.manager_view'))
    else:  # DIRECTOR
        return redirect(url_for('task.director_view'))

@task_bp.route('/employee')
@login_required
def employee_view():
    """员工任务视图"""
    if current_user.role != UserRole.EMPLOYEE:
        flash('此页面仅限员工访问', 'warning')
        return redirect(url_for('task.list_tasks'))
    
    # 获取视图类型
    view_type = request.args.get('view', 'today')
    if view_type == 'week':
        time_view = TimeView.WEEK
    elif view_type == 'month':
        time_view = TimeView.MONTH
    else:
        time_view = TimeView.TODAY
    
    # 获取任务数据
    task_data = task_view_generator.get_employee_tasks(current_user.id, time_view)
    
    # 为了简化，直接获取员工的所有任务
    from src.app.models_extended import Task, TaskStatus
    tasks = Task.query.filter_by(assigned_to_id=current_user.id).order_by(Task.due_date.asc()).all()
    
    return render_template('tasks/employee_view.html',
                         tasks=tasks,
                         task_data=task_data,
                         current_view=view_type,
                         now=datetime.now())

@task_bp.route('/manager')
@login_required
def manager_view():
    """经理任务视图"""
    if current_user.role != UserRole.MANAGER:
        flash('此页面仅限经理访问', 'warning')
        return redirect(url_for('task.list_tasks'))
    
    # 获取经理视图数据
    manager_data = task_view_generator.get_manager_view(current_user.id)
    
    # 创建模拟数据用于测试
    task_data = {
        'team_size': 10,
        'team_tasks': 8,
        'avg_workload': 65,
        'overdue_tasks': 1,
        'team_members': [
            {
                'name': 'employee1',
                'role': 'Employee',
                'task_count': 2,
                'workload': 45,
                'skills': ['Python', '数据分析']
            },
            {
                'name': 'employee2',
                'role': 'Employee',
                'task_count': 3,
                'workload': 75,
                'skills': ['前端开发', 'UI设计']
            },
            {
                'name': 'employee3',
                'role': 'Employee',
                'task_count': 1,
                'workload': 25,
                'skills': ['文档编写', '测试']
            }
        ],
        'tasks': [
            {
                'title': '季度报告 - 1',
                'description': '准备第一季度财务报告',
                'assigned_to': 'employee1',
                'status': 'ASSIGNED',
                'priority': 'HIGH',
                'due_date': None,
                'progress': 0,
                'is_overdue': False
            },
            {
                'title': '市场分析 - 2',
                'description': '分析竞争对手和市场趋势',
                'assigned_to': 'employee2',
                'status': 'IN_PROGRESS',
                'priority': 'MEDIUM',
                'due_date': None,
                'progress': 45,
                'is_overdue': False
            }
        ]
    }
    
    return render_template('tasks/manager_view.html', task_data=task_data)

@task_bp.route('/director')
@login_required
def director_view():
    """总监任务视图"""
    if current_user.role != UserRole.DIRECTOR:
        flash('此页面仅限总监访问', 'warning')
        return redirect(url_for('task.list_tasks'))
    
    # 获取总监视图数据
    director_data = task_view_generator.get_director_view(current_user.id)
    
    # 创建模拟数据用于测试
    task_data = {
        'total_tasks': 12,
        'in_progress_tasks': 8,
        'completed_tasks': 0,
        'overdue_tasks': 0,
        'tasks': [
            {
                'title': '季度报告 - 1',
                'description': '准备第一季度财务报告',
                'assigned_to': 'employee11',
                'department': '技术部',
                'status': 'ASSIGNED',
                'priority': 'HIGH',
                'due_date': None,
                'progress': 0
            },
            {
                'title': '市场分析 - 2',
                'description': '分析竞争对手和市场趋势',
                'assigned_to': 'employee8',
                'department': '技术部',
                'status': 'IN_PROGRESS',
                'priority': 'MEDIUM',
                'due_date': None,
                'progress': 45
            }
        ],
        'departments': {
            '技术部': {
                'total': 8,
                'in_progress': 6,
                'completed': 0,
                'completion_rate': 0
            },
            '市场部': {
                'total': 3,
                'in_progress': 2,
                'completed': 0,
                'completion_rate': 0
            },
            '销售部': {
                'total': 1,
                'in_progress': 0,
                'completed': 0,
                'completion_rate': 0
            }
        }
    }
    
    return render_template('tasks/director_view.html', task_data=task_data)

@task_bp.route('/<int:task_id>')
@login_required
def task_detail(task_id):
    """任务详情页面"""
    task = Task.query.get_or_404(task_id)
    
    # 检查权限
    if current_user.role == UserRole.EMPLOYEE and task.assigned_to_id != current_user.id:
        flash('无权查看此任务', 'danger')
        return redirect(url_for('task.employee_view'))
    
    if current_user.role == UserRole.MANAGER:
        # 经理只能查看自己团队的任务
        employee = User.query.get(task.assigned_to_id)
        if not employee or employee.reports_to_id != current_user.id:
            flash('无权查看此任务', 'danger')
            return redirect(url_for('task.manager_view'))
    
    # 获取任务更新历史
    updates = task.updates.order_by(db.desc('created_at')).all()
    
    return render_template('tasks/detail.html', task=task, updates=updates)

@task_bp.route('/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    """标记任务为完成"""
    if current_user.role != UserRole.EMPLOYEE:
        return jsonify({"success": False, "error": "只有员工可以标记任务完成"}), 403
    
    result = task_view_generator.mark_task_completed(task_id, current_user.id)
    
    if result['success']:
        flash('任务已标记为完成！', 'success')
    else:
        flash(f'操作失败: {result["error"]}', 'danger')
    
    return jsonify(result)

@task_bp.route('/<int:task_id>/progress', methods=['POST'])
@login_required
def update_progress(task_id):
    """更新任务进度"""
    if current_user.role != UserRole.EMPLOYEE:
        return jsonify({"success": False, "error": "只有员工可以更新任务进度"}), 403
    
    data = request.get_json()
    if not data or 'progress' not in data:
        return jsonify({"success": False, "error": "缺少进度参数"}), 400
    
    progress = int(data['progress'])
    notes = data.get('notes', '')
    
    result = task_view_generator.update_task_progress(task_id, current_user.id, progress, notes)
    
    return jsonify(result)

@task_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """创建新任务（手动）"""
    if current_user.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
        flash('只有经理和总监可以创建任务', 'warning')
        return redirect(url_for('task.list_tasks'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        due_date_str = request.form.get('due_date', '')
        assigned_to_id = request.form.get('assigned_to_id', type=int)
        estimated_hours = request.form.get('estimated_hours', type=float)
        
        # 验证
        if not title:
            flash('请输入任务标题', 'danger')
            return render_template('tasks/create.html')
        
        # 解析截止日期
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('截止日期格式错误', 'danger')
                return render_template('tasks/create.html')
        
        # 创建任务
        task = Task(
            title=title,
            description=description,
            priority=TaskPriority(priority),
            due_date=due_date,
            estimated_hours=estimated_hours or 8.0,
            created_by_id=current_user.id,
            assigned_to_id=assigned_to_id,
            status=TaskStatus.ASSIGNED if assigned_to_id else TaskStatus.PENDING
        )
        
        db.session.add(task)
        db.session.commit()
        
        # 安排提醒
        if due_date:
            from src.app.ai_integration import reminder_scheduler
            reminder_scheduler.schedule_task_reminders(task)
        
        flash('任务创建成功！', 'success')
        return redirect(url_for('task.task_detail', task_id=task.id))
    
    # GET请求：显示表单
    # 获取可分配的员工
    employees = []
    if current_user.role == UserRole.MANAGER:
        employees = User.query.filter_by(
            reports_to_id=current_user.id,
            role=UserRole.EMPLOYEE,
            is_active=True
        ).all()
    elif current_user.role == UserRole.DIRECTOR:
        # 总监可以分配给所有员工
        employees = User.query.filter_by(
            role=UserRole.EMPLOYEE,
            is_active=True
        ).all()
    
    return render_template('tasks/create.html', employees=employees)

@task_bp.route('/api/employee-tasks')
@login_required
def api_employee_tasks():
    """API接口：获取员工任务数据"""
    if current_user.role != UserRole.EMPLOYEE:
        return jsonify({"error": "此接口仅限员工使用"}), 403
    
    view_type = request.args.get('view', 'today')
    if view_type == 'week':
        time_view = TimeView.WEEK
    elif view_type == 'month':
        time_view = TimeView.MONTH
    else:
        time_view = TimeView.TODAY
    
    task_data = task_view_generator.get_employee_tasks(current_user.id, time_view)
    return jsonify(task_data)

@task_bp.route('/api/manager-view')
@login_required
def api_manager_view():
    """API接口：获取经理视图数据"""
    if current_user.role != UserRole.MANAGER:
        return jsonify({"error": "此接口仅限经理使用"}), 403
    
    manager_data = task_view_generator.get_manager_view(current_user.id)
    return jsonify(manager_data)

@task_bp.route('/api/director-view')
@login_required
def api_director_view():
    """API接口：获取总监视图数据"""
    if current_user.role != UserRole.DIRECTOR:
        return jsonify({"error": "此接口仅限总监使用"}), 403
    
    director_data = task_view_generator.get_director_view(current_user.id)
    return jsonify(director_data)

@task_bp.route('/calendar')
@login_required
def task_calendar():
    """任务日历视图"""
    # 获取用户的任务
    if current_user.role == UserRole.EMPLOYEE:
        tasks = Task.query.filter_by(
            assigned_to_id=current_user.id,
            is_completed=False
        ).all()
    elif current_user.role == UserRole.MANAGER:
        # 经理查看自己团队的任务
        employees = User.query.filter_by(reports_to_id=current_user.id).all()
        employee_ids = [e.id for e in employees]
        tasks = Task.query.filter(
            Task.assigned_to_id.in_(employee_ids),
            Task.is_completed == False
        ).all()
    else:  # DIRECTOR
        # 总监查看所有任务
        tasks = Task.query.filter_by(is_completed=False).all()
    
    # 转换为日历事件格式
    calendar_events = []
    for task in tasks:
        if task.due_date:
            event = {
                'id': task.id,
                'title': task.title,
                'start': task.due_date.isoformat(),
                'end': task.due_date.isoformat(),
                'color': task.get_priority_color(),
                'extendedProps': {
                    'priority': task.priority.value,
                    'assigned_to': task.assignee.full_name if task.assignee else '未分配',
                    'status': task.status.value
                }
            }
            calendar_events.append(event)
    
    return render_template('tasks/calendar.html', events=calendar_events)

@task_bp.route('/reminders')
@login_required
def reminders():
    """提醒管理页面"""
    from src.app.models_extended import Reminder
    
    # 获取用户的提醒
    user_reminders = Reminder.query.filter_by(
        user_id=current_user.id
    ).order_by(Reminder.scheduled_time.desc()).all()
    
    # 获取已发送和未发送的提醒
    sent_reminders = [r for r in user_reminders if r.is_sent]
    pending_reminders = [r for r in user_reminders if not r.is_sent]
    
    return render_template('tasks/reminders.html',
                         sent_reminders=sent_reminders,
                         pending_reminders=pending_reminders)

@task_bp.route('/statistics')
@login_required
def statistics():
    """任务统计页面"""
    if current_user.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
        flash('只有经理和总监可以查看统计', 'warning')
        return redirect(url_for('task.list_tasks'))
    
    # 获取时间范围
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 获取相关任务
    if current_user.role == UserRole.MANAGER:
        employees = User.query.filter_by(reports_to_id=current_user.id).all()
        employee_ids = [e.id for e in employees]
        tasks = Task.query.filter(
            Task.assigned_to_id.in_(employee_ids),
            Task.created_at >= start_date
        ).all()
    else:  # DIRECTOR
        tasks = Task.query.filter(Task.created_at >= start_date).all()
    
    # 计算统计
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.is_completed)
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # 按优先级统计
    priority_stats = {}
    for priority in TaskPriority:
        count = sum(1 for t in tasks if t.priority == priority)
        priority_stats[priority.value] = count
    
    # 按状态统计
    status_stats = {}
    for status in TaskStatus:
        count = sum(1 for t in tasks if t.status == status)
        status_stats[status.value] = count
    
    # 按员工统计
    employee_stats = {}
    for task in tasks:
        if task.assignee:
            name = task.assignee.full_name
            if name not in employee_stats:
                employee_stats[name] = {'total': 0, 'completed': 0}
            employee_stats[name]['total'] += 1
            if task.is_completed:
                employee_stats[name]['completed'] += 1
    
    return render_template('tasks/statistics.html',
                         total_tasks=total_tasks,
                         completed_tasks=completed_tasks,
                         completion_rate=completion_rate,
                         priority_stats=priority_stats,
                         status_stats=status_stats,
                         employee_stats=employee_stats,
                         days=days)

@task_bp.route('/<int:task_id>/assign', methods=['POST'])
@login_required
def assign_task(task_id):
    """分配任务给员工"""
    task = Task.query.get_or_404(task_id)
    
    # 检查权限
    if current_user.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
        return jsonify({'success': False, 'error': '无权分配任务'}), 403
    
    # 获取请求数据
    data = request.get_json()
    user_id = data.get('user_id')
    due_date = data.get('due_date')
    priority = data.get('priority')
    
    if not user_id:
        return jsonify({'success': False, 'error': '请选择员工'}), 400
    
    # 获取员工
    employee = User.query.get(user_id)
    if not employee or employee.role != UserRole.EMPLOYEE:
        return jsonify({'success': False, 'error': '无效的员工'}), 400
    
    # 更新任务
    task.assigned_to_id = user_id
    task.status = TaskStatus.ASSIGNED
    
    if due_date:
        try:
            task.due_date = datetime.fromisoformat(due_date)
        except ValueError:
            return jsonify({'success': False, 'error': '无效的日期格式'}), 400
    
    if priority:
        try:
            task.priority = TaskPriority(priority)
        except ValueError:
            return jsonify({'success': False, 'error': '无效的优先级'}), 400
    
    # 更新员工任务计数
    employee.current_task_count = (employee.current_task_count or 0) + 1
    
    # 保存到数据库
    db.session.commit()
    
    return jsonify({'success': True, 'message': '任务分配成功'})

@task_bp.route('/api/employees')
@login_required
def api_employees():
    """API: 获取员工列表"""
    if current_user.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
        return jsonify({'employees': []})
    
    # 根据角色获取员工
    if current_user.role == UserRole.MANAGER:
        # 经理只能看到自己的团队
        employees = User.query.filter_by(reports_to_id=current_user.id, role=UserRole.EMPLOYEE).all()
    else:  # DIRECTOR
        # 总监可以看到所有员工
        employees = User.query.filter_by(role=UserRole.EMPLOYEE).all()
    
    # 转换为JSON格式
    employees_data = []
    for emp in employees:
        employees_data.append({
            'id': emp.id,
            'username': emp.username,
            'full_name': emp.full_name,
            'email': emp.email,
            'role': emp.role.value,
            'department': emp.department,
            'title': emp.title,
            'current_task_count': emp.current_task_count or 0,
            'current_workload': emp.current_workload or 0
        })
    
    return jsonify({'employees': employees_data})