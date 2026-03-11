#!/usr/bin/env python3
"""简化初始化脚本 - 创建基本用户和测试数据"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app, db
from src.app.models_extended import User, UserRole, Task, TaskStatus, TaskPriority
from datetime import datetime, timedelta
import random

def create_basic_users():
    """创建基本用户"""
    print("创建基本用户...")
    
    # 创建总监
    director = User(
        username='director',
        email='director@company.com',
        full_name='张总监',
        role=UserRole.DIRECTOR,
        title='技术总监',
        department='技术部',
        current_task_count=0,
        weekly_capacity=40,
        current_workload=0,
        active=True
    )
    director.set_password('director123')
    
    # 创建经理
    managers = []
    for i in range(1, 5):
        manager = User(
            username=f'manager{i}',
            email=f'manager{i}@company.com',
            full_name=f'李经理{i}',
            role=UserRole.MANAGER,
            title='项目经理',
            department='技术部',
            reports_to_id=1,  # 总监的ID
            current_task_count=0,
            weekly_capacity=40,
            current_workload=0,
            active=True
        )
        manager.set_password(f'manager{i}123')
        managers.append(manager)
    
    # 创建员工
    employees = []
    employee_counter = 1
    for manager in managers:
        for j in range(1, 11):  # 每个经理10个员工
            employee = User(
                username=f'employee{employee_counter}',
                email=f'employee{employee_counter}@company.com',
                full_name=f'王员工{employee_counter}',
                role=UserRole.EMPLOYEE,
                title='开发工程师',
                department='技术部',
                reports_to_id=manager.id,
                current_task_count=0,
                weekly_capacity=40,
                current_workload=0,
                active=True
            )
            employee.set_password(f'employee{employee_counter}123')
            employees.append(employee)
            employee_counter += 1
    
    # 先提交所有用户，获取ID
    db.session.add(director)
    for manager in managers:
        db.session.add(manager)
    for employee in employees:
        db.session.add(employee)
    
    db.session.commit()
    
    print(f"✅ 用户创建完成: 总监1人, 经理4人, 员工40人")
    return director, managers, employees
    
    # 添加到数据库
    db.session.add(director)
    for manager in managers:
        db.session.add(manager)
    for employee in employees:
        db.session.add(employee)
    
    db.session.commit()
    
    print(f"✅ 用户创建完成: 总监1人, 经理4人, 员工40人")
    return director, managers, employees

def create_sample_tasks(director, managers, employees):
    """创建样本任务"""
    print("创建样本任务...")
    
    task_templates = [
        {"title": "季度报告", "desc": "准备季度财务报告", "hours": 20.0, "priority": TaskPriority.HIGH},
        {"title": "网站优化", "desc": "优化网站性能", "hours": 16.0, "priority": TaskPriority.MEDIUM},
        {"title": "客户调研", "desc": "进行客户满意度调研", "hours": 12.0, "priority": TaskPriority.URGENT},
        {"title": "市场分析", "desc": "分析新产品市场", "hours": 24.0, "priority": TaskPriority.HIGH},
        {"title": "团队培训", "desc": "组织团队技能培训", "hours": 8.0, "priority": TaskPriority.MEDIUM},
    ]
    
    task_count = 0
    
    # 为每个经理创建一些任务
    for manager in managers:
        # 获取该经理的员工
        manager_employees = [e for e in employees if e.reports_to_id == manager.id]
        if not manager_employees:
            continue
        
        for i in range(3):  # 每个经理3个任务
            template = random.choice(task_templates)
            assigned_employee = random.choice(manager_employees)
            
            task = Task(
                title=f"{template['title']} - {i+1}",
                description=template['desc'],
                priority=template['priority'],
                estimated_hours=template['hours'],
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
            load_increase = (task.estimated_hours / 40) * 100
            assigned_employee.current_workload = min(100, assigned_employee.current_workload + load_increase)
            assigned_employee.current_task_count += 1
    
    db.session.commit()
    print(f"✅ 样本任务创建完成: {task_count} 个任务")

def main():
    print("=" * 60)
    print("Work Distribution and Tracking System - 简化初始化")
    print("=" * 60)
    
    try:
        app = create_app()
        
        with app.app_context():
            # 创建数据库表
            print("创建数据库表...")
            db.create_all()
            
            # 创建用户
            director, managers, employees = create_basic_users()
            
            # 创建任务
            create_sample_tasks(director, managers, employees)
            
            print("\n" + "=" * 60)
            print("🎉 系统初始化完成！")
            print("\n登录凭证:")
            print(f"总监: username='director', password='director123'")
            print(f"经理1: username='manager1', password='manager1123'")
            print(f"员工1: username='employee1', password='employee1123'")
            print(f"员工10: username='employee10', password='employee10123'")
            print("\n访问 http://localhost:5001 开始使用系统")
            
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()