"""任务视图模块 - 生成今日/本周/本月视图，优先级颜色标识"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
from src.app import db
from src.app.models_extended import Task, TaskStatus, TaskPriority, User

class TimeView(Enum):
    """时间视图类型"""
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    ALL = "all"

@dataclass
class TaskViewItem:
    """任务视图项"""
    task_id: int
    title: str
    description: str
    priority: str
    priority_color: str
    due_date: Optional[datetime]
    due_date_color: str
    status: str
    progress: int
    assigned_to: str
    assigned_to_id: int
    estimated_hours: float
    actual_hours: float
    time_view: str  # today/week/month
    days_left: Optional[int]
    is_completed: bool
    current_step: int
    total_steps: int

class TaskViewGenerator:
    """任务视图生成器"""
    
    def __init__(self):
        self.today = datetime.utcnow().date()
    
    def get_employee_tasks(self, employee_id: int, view_type: TimeView = TimeView.TODAY) -> Dict[str, Any]:
        """
        获取员工的任务视图
        
        Args:
            employee_id: 员工ID
            view_type: 视图类型
            
        Returns:
            任务视图数据
        """
        employee = User.query.get(employee_id)
        if not employee:
            return {"error": "员工不存在"}
        
        # 获取员工的所有任务
        all_tasks = Task.query.filter_by(
            assigned_to_id=employee_id,
            is_completed=False
        ).order_by(
            Task.priority,
            Task.due_date
        ).all()
        
        # 分类任务
        tasks_by_view = self._categorize_tasks_by_time(all_tasks)
        
        # 根据请求的视图类型返回数据
        if view_type == TimeView.TODAY:
            tasks = tasks_by_view["today"]
        elif view_type == TimeView.WEEK:
            tasks = tasks_by_view["week"]
        elif view_type == TimeView.MONTH:
            tasks = tasks_by_view["month"]
        else:  # ALL
            tasks = all_tasks
        
        # 转换为视图项
        view_items = [self._task_to_view_item(task) for task in tasks]
        
        # 统计信息
        stats = self._calculate_task_stats(tasks_by_view, all_tasks)
        
        return {
            "employee": {
                "id": employee.id,
                "name": employee.full_name,
                "username": employee.username,
                "current_task_count": employee.current_task_count,
                "current_workload": employee.current_workload,
                "workload_color": employee.get_workload_color()
            },
            "tasks": [item.__dict__ for item in view_items],
            "stats": stats,
            "view_type": view_type.value,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def get_manager_view(self, manager_id: int) -> Dict[str, Any]:
        """
        获取经理视图 - 查看下属员工的任务情况
        
        Args:
            manager_id: 经理ID
            
        Returns:
            经理视图数据
        """
        manager = User.query.get(manager_id)
        if not manager:
            return {"error": "经理不存在"}
        
        # 获取下属员工
        employees = User.query.filter_by(
            reports_to_id=manager_id,
            is_active=True
        ).all()
        
        employee_data = []
        total_tasks = 0
        total_workload = 0.0
        
        for employee in employees:
            # 获取员工的任务统计
            tasks = Task.query.filter_by(
                assigned_to_id=employee.id,
                is_completed=False
            ).all()
            
            # 分类任务
            tasks_by_view = self._categorize_tasks_by_time(tasks)
            
            # 计算统计
            task_stats = self._calculate_task_stats(tasks_by_view, tasks)
            
            employee_data.append({
                "id": employee.id,
                "name": employee.full_name,
                "username": employee.username,
                "task_count": len(tasks),
                "workload_percentage": employee.current_workload,
                "workload_color": employee.get_workload_color(),
                "task_stats": task_stats,
                "today_tasks": len(tasks_by_view["today"]),
                "week_tasks": len(tasks_by_view["week"]),
                "month_tasks": len(tasks_by_view["month"])
            })
            
            total_tasks += len(tasks)
            total_workload += employee.current_workload
        
        # 计算平均工作负载
        avg_workload = total_workload / len(employees) if employees else 0
        
        # 获取需要关注的紧急任务
        urgent_tasks = Task.query.filter(
            Task.assigned_to_id.in_([e.id for e in employees]),
            Task.priority == TaskPriority.URGENT,
            Task.is_completed == False,
            Task.status != TaskStatus.COMPLETED
        ).order_by(Task.due_date).limit(10).all()
        
        return {
            "manager": {
                "id": manager.id,
                "name": manager.full_name,
                "employee_count": len(employees)
            },
            "employees": employee_data,
            "summary": {
                "total_employees": len(employees),
                "total_tasks": total_tasks,
                "average_workload": avg_workload,
                "urgent_task_count": len(urgent_tasks)
            },
            "urgent_tasks": [self._task_to_view_item(task).__dict__ for task in urgent_tasks],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def get_director_view(self, director_id: int) -> Dict[str, Any]:
        """
        获取总监视图 - 查看整个组织的情况
        
        Args:
            director_id: 总监ID
            
        Returns:
            总监视图数据
        """
        director = User.query.get(director_id)
        if not director or director.role.value != "director":
            return {"error": "总监不存在或不是总监"}
        
        # 获取所有经理
        managers = User.query.filter_by(
            reports_to_id=director_id,
            role="manager",
            is_active=True
        ).all()
        
        # 获取所有员工
        all_employees = User.query.filter(
            User.reports_to_id.in_([m.id for m in managers]),
            User.is_active == True
        ).all()
        
        manager_data = []
        total_employees = 0
        total_tasks = 0
        department_stats = {}
        
        for manager in managers:
            # 获取该经理的团队数据
            employees = User.query.filter_by(
                reports_to_id=manager.id,
                is_active=True
            ).all()
            
            team_tasks = Task.query.filter(
                Task.assigned_to_id.in_([e.id for e in employees]),
                Task.is_completed == False
            ).all()
            
            # 计算团队工作负载
            team_workload = sum(e.current_workload for e in employees) / len(employees) if employees else 0
            
            # 紧急任务统计
            urgent_tasks = Task.query.filter(
                Task.assigned_to_id.in_([e.id for e in employees]),
                Task.priority == TaskPriority.URGENT,
                Task.is_completed == False
            ).count()
            
            manager_data.append({
                "id": manager.id,
                "name": manager.full_name,
                "employee_count": len(employees),
                "team_workload": team_workload,
                "task_count": len(team_tasks),
                "urgent_tasks": urgent_tasks,
                "workload_color": self._get_workload_color(team_workload)
            })
            
            total_employees += len(employees)
            total_tasks += len(team_tasks)
            
            # 部门统计
            dept = manager.department or "未分配"
            if dept not in department_stats:
                department_stats[dept] = {
                    "manager_count": 0,
                    "employee_count": 0,
                    "task_count": 0
                }
            department_stats[dept]["manager_count"] += 1
            department_stats[dept]["employee_count"] += len(employees)
            department_stats[dept]["task_count"] += len(team_tasks)
        
        # 整体统计
        completed_tasks_week = Task.query.filter(
            Task.is_completed == True,
            Task.completed_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        overdue_tasks = Task.query.filter(
            Task.is_completed == False,
            Task.due_date < datetime.utcnow()
        ).count()
        
        return {
            "director": {
                "id": director.id,
                "name": director.full_name
            },
            "organization_summary": {
                "manager_count": len(managers),
                "employee_count": total_employees,
                "total_tasks": total_tasks,
                "completed_this_week": completed_tasks_week,
                "overdue_tasks": overdue_tasks,
                "department_count": len(department_stats)
            },
            "managers": manager_data,
            "departments": department_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _categorize_tasks_by_time(self, tasks: List[Task]) -> Dict[str, List[Task]]:
        """根据时间分类任务"""
        today_tasks = []
        week_tasks = []
        month_tasks = []
        
        for task in tasks:
            if not task.due_date:
                month_tasks.append(task)
                continue
            
            days_left = (task.due_date.date() - self.today).days
            
            if days_left == 0:
                today_tasks.append(task)
            elif 0 < days_left <= 7:
                week_tasks.append(task)
            else:
                month_tasks.append(task)
        
        return {
            "today": today_tasks,
            "week": week_tasks,
            "month": month_tasks
        }
    
    def _task_to_view_item(self, task: Task) -> TaskViewItem:
        """将任务转换为视图项"""
        
        # 计算剩余天数
        days_left = None
        if task.due_date:
            days_left = (task.due_date.date() - self.today).days
        
        # 确定时间视图
        time_view = "month"  # 默认
        if days_left is not None:
            if days_left == 0:
                time_view = "today"
            elif 0 < days_left <= 7:
                time_view = "week"
        
        return TaskViewItem(
            task_id=task.id,
            title=task.title,
            description=task.description or "",
            priority=task.priority.value,
            priority_color=task.get_priority_color(),
            due_date=task.due_date,
            due_date_color=task.get_due_date_color(),
            status=task.status.value,
            progress=task.progress,
            assigned_to=task.assignee.full_name if task.assignee else "未分配",
            assigned_to_id=task.assigned_to_id or 0,
            estimated_hours=task.estimated_hours or 0.0,
            actual_hours=task.actual_hours or 0.0,
            time_view=time_view,
            days_left=days_left,
            is_completed=task.is_completed,
            current_step=task.current_step,
            total_steps=task.total_steps
        )
    
    def _calculate_task_stats(self, tasks_by_view: Dict[str, List[Task]], all_tasks: List[Task]) -> Dict[str, Any]:
        """计算任务统计信息"""
        
        total_tasks = len(all_tasks)
        
        # 按优先级统计
        priority_stats = {
            "urgent": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for task in all_tasks:
            priority_stats[task.priority.value] += 1
        
        # 按状态统计
        status_stats = {
            "pending": 0,
            "assigned": 0,
            "in_progress": 0,
            "completed": 0
        }
        
        for task in all_tasks:
            status_stats[task.status.value] += 1
        
        # 总预估工时
        total_estimated_hours = sum(task.estimated_hours or 0 for task in all_tasks)
        
        # 总实际工时
        total_actual_hours = sum(task.actual_hours or 0 for task in all_tasks)
        
        return {
            "total_tasks": total_tasks,
            "today_tasks": len(tasks_by_view["today"]),
            "week_tasks": len(tasks_by_view["week"]),
            "month_tasks": len(tasks_by_view["month"]),
            "priority_distribution": priority_stats,
            "status_distribution": status_stats,
            "total_estimated_hours": total_estimated_hours,
            "total_actual_hours": total_actual_hours,
            "completion_rate": (total_actual_hours / total_estimated_hours * 100) if total_estimated_hours > 0 else 0
        }
    
    def _get_workload_color(self, workload: float) -> str:
        """根据工作负载获取颜色"""
        if workload >= 90:
            return 'danger'
        elif workload >= 70:
            return 'warning'
        elif workload >= 50:
            return 'info'
        else:
            return 'success'
    
    def mark_task_completed(self, task_id: int, employee_id: int) -> Dict[str, Any]:
        """标记任务为完成"""
        task = Task.query.get(task_id)
        if not task:
            return {"success": False, "error": "任务不存在"}
        
        if task.assigned_to_id != employee_id:
            return {"success": False, "error": "无权完成此任务"}
        
        # 更新任务状态
        task.is_completed = True
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.progress = 100
        
        # 更新员工工作负载
        employee = User.query.get(employee_id)
        if employee and task.estimated_hours:
            # 减少工作负载（简化计算）
            weekly_hours = 40
            load_reduction = (task.estimated_hours / weekly_hours) * 100
            employee.current_workload = max(0, employee.current_workload - load_reduction)
            employee.current_task_count = max(0, employee.current_task_count - 1)
        
        # 创建任务更新记录
        from src.app.models_extended import TaskUpdate
        update = TaskUpdate(
            task_id=task_id,
            user_id=employee_id,
            old_status=task.status,
            new_status=TaskStatus.COMPLETED,
            old_progress=task.progress,
            new_progress=100,
            notes="任务已完成"
        )
        db.session.add(update)
        
        db.session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "task_title": task.title,
            "completed_at": task.completed_at.isoformat(),
            "employee_workload": employee.current_workload if employee else 0
        }
    
    def update_task_progress(self, task_id: int, employee_id: int, progress: int, notes: str = "") -> Dict[str, Any]:
        """更新任务进度"""
        if progress < 0 or progress > 100:
            return {"success": False, "error": "进度必须在0-100之间"}
        
        task = Task.query.get(task_id)
        if not task:
            return {"success": False, "error": "任务不存在"}
        
        if task.assigned_to_id != employee_id:
            return {"success": False, "error": "无权更新此任务"}
        
        old_progress = task.progress
        old_status = task.status
        
        # 更新任务
        task.progress = progress
        
        # 根据进度更新状态
        if progress == 100:
            task.status = TaskStatus.COMPLETED
            task.is_completed = True
            task.completed_at = datetime.utcnow()
        elif progress > 0:
            task.status = TaskStatus.IN_PROGRESS
        else:
            task.status = TaskStatus.ASSIGNED
        
        # 创建更新记录
        from src.app.models_extended import TaskUpdate
        update = TaskUpdate(
            task_id=task_id,
            user_id=employee_id,
            old_status=old_status,
            new_status=task.status,
            old_progress=old_progress,
            new_progress=progress,
            notes=notes
        )
        db.session.add(update)
        
        db.session.commit()
        
        return {
            "success": True,
            "task_id": task_id,
            "progress": progress,
            "status": task.status.value,
            "updated_at": datetime.utcnow().isoformat()
        }

# 全局实例
task_view_generator = TaskViewGenerator()