#!/usr/bin/env python3
"""初始化系统 - 创建默认组织架构和测试数据"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app, db
from src.app.models_extended import User, UserRole, Task, TaskStatus, TaskPriority, OrganizationNode
from src.app.organization_chart import OrganizationChart
from datetime import datetime, timedelta
import random

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    app = create_app()
    
    with app.app_context():
        # 删除现有数据
        print("清理现有数据...")
        db.drop_all()
        db.create_all()
        
        # 创建组织架构
        print("创建组织架构...")
        org_chart = OrganizationChart()
        director = org_chart._create_default_organization()
        
        print(f"✅ 总监创建成功: {director.full_name}")
        
        # 获取所有用户
        users = User.query.all()
        print(f"✅ 用户创建完成: 总监1人, 经理4人, 员工40人")
        
        # 为每个用户创建组织节点
        for user in users:
            org_chart._get_or_create_node(user)
        
        # 生成组织架构图
        chart_data = org_chart.generate_chart_data(director.id)
        print("✅ 组织架构图生成完成")
        
        # 创建一些测试任务
        print("创建测试任务...")
        create_sample_tasks(users, director)
        
        print("\n🎉 系统初始化完成！")
        print("\n登录凭证:")
        print(f"总监: username='director', password='director123'")
        print(f"经理1: username='manager1', password='manager1123'")
        print(f"员工1: username='employee1', password='employee1123'")
        print(f"员工10: username='employee10', password='employee10123'")
        print("\n访问 http://localhost:5001 开始使用系统")

def create_sample_tasks(users, director):
    """创建样本任务"""
    
    # 任务模板
    task_templates = [
        {
            "title": "季度财务报告",
            "description": "准备公司季度财务报告，包括收入、支出和利润分析",
            "priority": TaskPriority.HIGH,
            "estimated_hours": 20.0
        },
        {
            "title": "网站性能优化",
            "description": "优化公司网站加载速度，减少页面加载时间",
            "priority": TaskPriority.MEDIUM,
            "estimated_hours": 16.0
        },
        {
            "title": "客户满意度调查",
            "description": "设计和实施客户满意度调查，分析结果并提出改进建议",
            "priority": TaskPriority.URGENT,
            "estimated_hours": 12.0
        },
        {
            "title": "新产品市场调研",
            "description": "调研新产品市场潜力，分析竞争对手和客户需求",
            "priority": TaskPriority.HIGH,
            "estimated_hours": 24.0
        },
        {
            "title": "团队培训计划",
            "description": "制定团队技能培训计划，提升团队整体能力",
            "priority": TaskPriority.MEDIUM,
            "estimated_hours": 8.0
        },
        {
            "title": "系统安全审计",
            "description": "进行系统安全审计，发现并修复潜在安全漏洞",
            "priority": TaskPriority.URGENT,
            "estimated_hours": 18.0
        },
        {
            "title": "社交媒体营销",
            "description": "制定并执行社交媒体营销策略，提升品牌知名度",
            "priority": TaskPriority.LOW,
            "estimated_hours": 10.0
        },
        {
            "title": "数据库迁移",
            "description": "将旧数据库迁移到新系统，确保数据完整性和一致性",
            "priority": TaskPriority.HIGH,
            "estimated_hours": 32.0
        },
        {
            "title": "员工绩效考核",
            "description": "进行季度员工绩效考核，提供反馈和发展建议",
            "priority": TaskPriority.MEDIUM,
            "estimated_hours": 15.0
        },
        {
            "title": "新产品发布准备",
            "description": "准备新产品发布材料，包括文档、演示和培训",
            "priority": TaskPriority.URGENT,
            "estimated_hours": 28.0
        }
    ]
    
    # 按角色分组用户
    directors = [u for u in users if u.role == UserRole.DIRECTOR]
    managers = [u for u in users if u.role == UserRole.MANAGER]
    employees = [u for u in users if u.role == UserRole.EMPLOYEE]
    
    task_count = 0
    
    # 为每个经理创建一些任务
    for manager in managers:
        # 经理创建的任务
        for i in range(3):
            template = random.choice(task_templates)
            
            # 选择该经理的员工
            manager_employees = [e for e in employees if e.reports_to_id == manager.id]
            if not manager_employees:
                continue
            
            assigned_employee = random.choice(manager_employees)
            
            task = Task(
                title=f"{template['title']} - {i+1}",
                description=template['description'],
                priority=template['priority'],
                estimated_hours=template['estimated_hours'],
                due_date=datetime.utcnow() + timedelta(days=random.randint(7, 30)),
                created_by_id=manager.id,
                assigned_to_id=assigned_employee.id,
                status=TaskStatus.IN_PROGRESS if random.random() > 0.5 else TaskStatus.ASSIGNED,
                progress=random.randint(0, 100) if random.random() > 0.3 else 0
            )
            
            if task.progress == 100:
                task.is_completed = True
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow() - timedelta(days=random.randint(1, 7))
            
            db.session.add(task)
            task_count += 1
            
            # 更新员工工作负载
            weekly_hours = 40
            load_increase = (task.estimated_hours / weekly_hours) * 100
            assigned_employee.current_workload = min(100, assigned_employee.current_workload + load_increase)
            assigned_employee.current_task_count += 1
    
    # 为总监创建一些任务
    for i in range(2):
        template = random.choice(task_templates)
        
        # 总监可以分配给任何经理
        assigned_manager = random.choice(managers)
        
        task = Task(
            title=f"[总监] {template['title']}",
            description=f"总监直接分配的任务: {template['description']}",
            priority=template['priority'],
            estimated_hours=template['estimated_hours'],
            due_date=datetime.utcnow() + timedelta(days=random.randint(14, 60)),
            created_by_id=director.id,
            assigned_to_id=assigned_manager.id,
            status=TaskStatus.ASSIGNED,
            progress=0
        )
        
        db.session.add(task)
        task_count += 1
        
        # 更新经理工作负载
        weekly_hours = 40
        load_increase = (task.estimated_hours / weekly_hours) * 100
        assigned_manager.current_workload = min(100, assigned_manager.current_workload + load_increase)
        assigned_manager.current_task_count += 1
    
    db.session.commit()
    print(f"✅ 测试任务创建完成: {task_count} 个任务")

def check_system_status():
    """检查系统状态"""
    print("\n🔍 检查系统状态...")
    
    app = create_app()
    
    with app.app_context():
        # 统计用户
        total_users = User.query.count()
        directors = User.query.filter_by(role=UserRole.DIRECTOR).count()
        managers = User.query.filter_by(role=UserRole.MANAGER).count()
        employees = User.query.filter_by(role=UserRole.EMPLOYEE).count()
        
        print(f"用户统计: 总监{directors}人, 经理{managers}人, 员工{employees}人")
        
        # 统计任务
        total_tasks = Task.query.count()
        completed_tasks = Task.query.filter_by(is_completed=True).count()
        pending_tasks = Task.query.filter_by(is_completed=False).count()
        
        print(f"任务统计: 总计{total_tasks}个, 已完成{completed_tasks}个, 待完成{pending_tasks}个")
        
        # 检查组织节点
        org_nodes = OrganizationNode.query.count()
        print(f"组织节点: {org_nodes}个")
        
        # 检查工作负载
        avg_workload = db.session.query(db.func.avg(User.current_workload)).scalar() or 0
        print(f"平均工作负载: {avg_workload:.1f}%")
        
        if total_users >= 45 and total_tasks >= 10:
            print("✅ 系统状态正常")
            return True
        else:
            print("⚠️  系统状态异常，建议重新初始化")
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("Work Distribution and Tracking System - 系统初始化")
    print("=" * 60)
    
    try:
        init_database()
        
        # 检查系统状态
        if check_system_status():
            print("\n🎊 系统初始化成功！")
            print("\n下一步:")
            print("1. 启动服务器: python run.py")
            print("2. 访问 http://localhost:5001")
            print("3. 使用上面提供的凭证登录")
            print("4. 开始使用AI任务分析和组织架构管理功能")
        else:
            print("\n❌ 系统初始化可能有问题，请检查日志")
            
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)