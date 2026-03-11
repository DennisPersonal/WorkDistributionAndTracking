"""组织架构相关路由"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from src.app import db
from src.app.models_extended import User, UserRole
from src.app.organization_chart import org_chart

org_bp = Blueprint('org', __name__, url_prefix='/org')

@org_bp.route('/chart')
@login_required
def organization_chart():
    """组织架构图页面"""
    if current_user.role != UserRole.DIRECTOR:
        flash('只有总监可以查看完整组织架构图', 'warning')
        return redirect(url_for('org.employee_view'))
    
    # 获取所有用户作为简单组织架构数据
    from src.app.models_extended import User
    users = User.query.all()
    
    # 获取总监
    director = User.query.filter_by(role=UserRole.DIRECTOR).first()
    
    # 构建层次结构数据
    chart_data = []
    
    # 添加总监
    if director:
        chart_data.append({
            'id': director.id,
            'username': director.username,
            'full_name': director.full_name or director.username,
            'role': 'DIRECTOR',
            'department': director.department or 'Management',
            'current_workload': float(director.current_workload or 0),
            'current_task_count': director.current_task_count or 0,
            'reports_to_id': None,
            'level': 1,
            'employee_count': User.query.filter_by(reports_to_id=director.id, role=UserRole.MANAGER).count(),
            'manager_id': None,
            'children': []
        })
    
    # 添加经理
    managers = User.query.filter_by(role=UserRole.MANAGER).all()
    for manager in managers:
        # 计算下属员工数量
        employee_count = User.query.filter_by(reports_to_id=manager.id, role=UserRole.EMPLOYEE).count()
        
        chart_data.append({
            'id': manager.id,
            'username': manager.username,
            'full_name': manager.full_name or manager.username,
            'role': 'MANAGER',
            'department': manager.department or 'Department',
            'current_workload': float(manager.current_workload or 0),
            'current_task_count': manager.current_task_count or 0,
            'reports_to_id': manager.reports_to_id,
            'level': 2,
            'employee_count': employee_count,
            'manager_id': director.id if director else None,
            'children': []
        })
    
    # 添加员工
    employees = User.query.filter_by(role=UserRole.EMPLOYEE).all()
    for employee in employees:
        chart_data.append({
            'id': employee.id,
            'username': employee.username,
            'full_name': employee.full_name or employee.username,
            'role': 'EMPLOYEE',
            'department': employee.department or 'Team',
            'current_workload': float(employee.current_workload or 0),
            'current_task_count': employee.current_task_count or 0,
            'reports_to_id': employee.reports_to_id,
            'level': 3,
            'employee_count': 0,
            'manager_id': employee.reports_to_id,
            'children': []
        })
    
    # 构建层次结构
    hierarchical_data = []
    
    # 添加总监
    if director:
        director_node = next((u for u in chart_data if u['role'] == 'DIRECTOR'), None)
        if director_node:
            # 添加下属经理
            for manager in [u for u in chart_data if u['role'] == 'MANAGER' and u['manager_id'] == director.id]:
                # 添加下属员工
                manager['children'] = [u for u in chart_data if u['role'] == 'EMPLOYEE' and u['manager_id'] == manager['id']]
                director_node['children'].append(manager)
            
            hierarchical_data.append(director_node)
    
    return render_template('org/chart.html', 
                         chart_data=chart_data,
                         hierarchical_data=hierarchical_data)

@org_bp.route('/employee-view')
@login_required
def employee_view():
    """员工视图的组织架构"""
    from src.app.models_extended import User
    
    # 获取当前用户的经理
    manager = None
    if current_user.reports_to_id:
        manager = User.query.get(current_user.reports_to_id)
    
    # 获取团队成员
    team_members = []
    if current_user.role == UserRole.MANAGER:
        # 经理查看自己的团队
        team_members = User.query.filter_by(reports_to_id=current_user.id).all()
    elif current_user.role == UserRole.EMPLOYEE and manager:
        # 员工查看同经理的同事
        team_members = User.query.filter_by(reports_to_id=manager.id).all()
    
    # 计算团队大小
    team_size = len(team_members)
    
    return render_template('org/employee_view.html', 
                          manager=manager,
                          team_members=team_members,
                          team_size=team_size)

@org_bp.route('/api/chart-data')
@login_required
def api_chart_data():
    """API接口：获取组织架构数据"""
    if current_user.role == UserRole.DIRECTOR:
        chart_data = org_chart.generate_chart_data(current_user.id)
    elif current_user.role == UserRole.MANAGER:
        chart_data = org_chart.generate_chart_data()
        # 经理只能看到自己团队
        team_member_ids = [current_user.id]
        employees = User.query.filter_by(reports_to_id=current_user.id).all()
        team_member_ids.extend([e.id for e in employees])
        
        chart_data['nodes'] = [
            node for node in chart_data['nodes']
            if node['user_id'] in team_member_ids
        ]
        
        chart_data['edges'] = [
            edge for edge in chart_data['edges']
            if any(node['user_id'] in team_member_ids for node in chart_data['nodes'] if node['id'] in [edge['from'], edge['to']])
        ]
    else:
        chart_data = org_chart.get_employee_view_data(current_user.id)
    
    return jsonify(chart_data)

@org_bp.route('/api/update-position', methods=['POST'])
@login_required
def api_update_position():
    """API接口：更新节点位置（拖拽后）"""
    if current_user.role != UserRole.DIRECTOR:
        return jsonify({"success": False, "error": "只有总监可以调整组织架构"}), 403
    
    data = request.get_json()
    if not data or 'node_id' not in data or 'x' not in data or 'y' not in data:
        return jsonify({"success": False, "error": "缺少参数"}), 400
    
    node_id = data['node_id']
    x = float(data['x'])
    y = float(data['y'])
    
    success = org_chart.update_node_position(node_id, x, y)
    
    if success:
        return jsonify({"success": True, "message": "位置已更新"})
    else:
        return jsonify({"success": False, "error": "更新失败"}), 400

@org_bp.route('/api/update-reporting', methods=['POST'])
@login_required
def api_update_reporting():
    """API接口：更新汇报关系（拖拽改变上级）"""
    if current_user.role != UserRole.DIRECTOR:
        return jsonify({"success": False, "error": "只有总监可以调整汇报关系"}), 403
    
    data = request.get_json()
    if not data or 'employee_id' not in data or 'new_manager_id' not in data:
        return jsonify({"success": False, "error": "缺少参数"}), 400
    
    employee_id = data['employee_id']
    new_manager_id = data['new_manager_id']
    
    result = org_chart.update_reporting_line(employee_id, new_manager_id)
    
    if result['success']:
        # 重新生成图表数据
        chart_data = org_chart.generate_chart_data(current_user.id)
        result['chart_data'] = chart_data
        
        flash(f"已更新 {result['employee_name']} 的汇报关系", 'success')
    
    return jsonify(result)

@org_bp.route('/management')
@login_required
def management():
    """组织架构管理页面"""
    if current_user.role != UserRole.DIRECTOR:
        flash('只有总监可以管理组织架构', 'warning')
        return redirect(url_for('main.dashboard'))
    
    # 获取所有用户
    users = User.query.filter_by(is_active=True).order_by(User.role, User.full_name).all()
    
    # 按角色分组
    directors = [u for u in users if u.role == UserRole.DIRECTOR]
    managers = [u for u in users if u.role == UserRole.MANAGER]
    employees = [u for u in users if u.role == UserRole.EMPLOYEE]
    
    # 统计信息
    stats = {
        'total_users': len(users),
        'director_count': len(directors),
        'manager_count': len(managers),
        'employee_count': len(employees),
        'avg_workload': sum(u.current_workload for u in users) / len(users) if users else 0
    }
    
    return render_template('org/management.html',
                         directors=directors,
                         managers=managers,
                         employees=employees,
                         stats=stats)

@org_bp.route('/api/user/<int:user_id>')
@login_required
def api_user_info(user_id):
    """API接口：获取用户信息"""
    user = User.query.get_or_404(user_id)
    
    # 检查权限
    if current_user.role == UserRole.EMPLOYEE and user_id != current_user.id:
        return jsonify({"error": "无权查看其他用户信息"}), 403
    
    if current_user.role == UserRole.MANAGER:
        # 经理只能查看自己团队的用户
        team_member_ids = [current_user.id]
        employees = User.query.filter_by(reports_to_id=current_user.id).all()
        team_member_ids.extend([e.id for e in employees])
        
        if user_id not in team_member_ids:
            return jsonify({"error": "无权查看此用户信息"}), 403
    
    user_data = {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'email': user.email,
        'role': user.role.value,
        'title': user.title,
        'department': user.department,
        'reports_to': user.reports_to.full_name if user.reports_to else None,
        'reports_to_id': user.reports_to_id,
        'current_task_count': user.current_task_count,
        'current_workload': user.current_workload,
        'workload_color': user.get_workload_color(),
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }
    
    return jsonify(user_data)

@org_bp.route('/api/update-user', methods=['POST'])
@login_required
def api_update_user():
    """API接口：更新用户信息"""
    if current_user.role != UserRole.DIRECTOR:
        return jsonify({"success": False, "error": "只有总监可以更新用户信息"}), 403
    
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"success": False, "error": "缺少用户ID"}), 400
    
    user_id = data['user_id']
    user = User.query.get_or_404(user_id)
    
    # 更新字段
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'title' in data:
        user.title = data['title']
    if 'department' in data:
        user.department = data['department']
    if 'reports_to_id' in data:
        user.reports_to_id = data['reports_to_id']
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "用户信息已更新",
        "user_id": user_id
    })

@org_bp.route('/workload')
@login_required
def workload_view():
    """工作负载视图"""
    if current_user.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
        flash('只有经理和总监可以查看工作负载', 'warning')
        return redirect(url_for('main.dashboard'))
    
    # 获取相关用户
    if current_user.role == UserRole.DIRECTOR:
        # 总监查看所有经理和员工
        users = User.query.filter(
            User.role.in_([UserRole.MANAGER, UserRole.EMPLOYEE]),
            User.is_active == True
        ).order_by(User.role, User.current_workload.desc()).all()
    else:
        # 经理查看自己团队的员工
        users = User.query.filter_by(
            reports_to_id=current_user.id,
            is_active=True
        ).order_by(User.current_workload.desc()).all()
    
    # 计算统计
    total_users = len(users)
    total_workload = sum(u.current_workload for u in users)
    avg_workload = total_workload / total_users if total_users > 0 else 0
    
    # 按工作负载等级分组
    workload_levels = {
        'overloaded': [u for u in users if u.current_workload >= 90],
        'high': [u for u in users if 70 <= u.current_workload < 90],
        'medium': [u for u in users if 50 <= u.current_workload < 70],
        'low': [u for u in users if u.current_workload < 50]
    }
    
    return render_template('org/workload.html',
                         users=users,
                         total_users=total_users,
                         avg_workload=avg_workload,
                         workload_levels=workload_levels)