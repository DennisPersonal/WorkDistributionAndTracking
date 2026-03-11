"""扩展的数据模型 - 基于新需求"""

from datetime import datetime, timedelta
from enum import Enum
from src.app import db
import json

class UserRole(Enum):
    """用户角色枚举"""
    DIRECTOR = 'director'     # 总监
    MANAGER = 'manager'      # 老板/经理
    EMPLOYEE = 'employee'    # 员工
    
class TaskPriority(Enum):
    """任务优先级枚举"""
    URGENT = 'urgent'    # 紧急 - 红色
    HIGH = 'high'        # 高   - 橙色
    MEDIUM = 'medium'    # 中   - 黄色
    LOW = 'low'          # 低   - 绿色

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = 'pending'          # 待分配
    ASSIGNED = 'assigned'        # 已分配
    IN_PROGRESS = 'in_progress'  # 进行中
    COMPLETED = 'completed'      # 已完成
    CANCELLED = 'cancelled'      # 已取消

class User(db.Model):
    """扩展的用户模型 - 支持组织架构"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(128))
    
    # 组织架构字段
    role = db.Column(db.Enum(UserRole), default=UserRole.EMPLOYEE)
    title = db.Column(db.String(64))  # 职位名称
    department = db.Column(db.String(64))  # 部门
    
    # 汇报关系
    reports_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # 工作负载统计
    current_task_count = db.Column(db.Integer, default=0)
    weekly_capacity = db.Column(db.Integer, default=40)  # 每周工作小时数
    current_workload = db.Column(db.Float, default=0.0)  # 当前负荷百分比
    
    # 状态
    active = db.Column(db.Boolean, default=True)  # 重命名为active以避免与Flask-Login冲突
    last_login = db.Column(db.DateTime)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    reports_to = db.relationship('User', remote_side=[id], backref='subordinates')
    
    # 任务关系
    tasks_assigned = db.relationship('Task', foreign_keys='Task.assigned_to_id', backref='assignee', lazy='dynamic')
    tasks_created = db.relationship('Task', foreign_keys='Task.created_by_id', backref='creator', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """检查密码"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    # Flask-Login required methods
    @property
    def is_authenticated(self):
        """检查用户是否已认证"""
        return True
    
    @property
    def is_active(self):
        """检查用户是否激活"""
        return self.active  # 返回重命名的数据库字段
    
    @property
    def is_anonymous(self):
        """检查用户是否匿名"""
        return False
    
    def get_id(self):
        """获取用户ID（Flask-Login要求）"""
        return str(self.id)
    
    def get_workload_color(self):
        """获取工作负载颜色"""
        if self.current_workload >= 90:
            return 'danger'     # 红色 - 超负荷
        elif self.current_workload >= 70:
            return 'warning'    # 黄色 - 高负荷
        elif self.current_workload >= 50:
            return 'info'       # 蓝色 - 中等负荷
        else:
            return 'success'    # 绿色 - 低负荷
    
    def __repr__(self):
        return f'<User {self.username} ({self.role.value})>'

class OrganizationNode(db.Model):
    """组织架构节点 - 用于可视化"""
    __tablename__ = 'organization_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 可视化位置
    x = db.Column(db.Float, default=0.0)
    y = db.Column(db.Float, default=0.0)
    
    # 层级
    level = db.Column(db.Integer, default=0)  # 0:总监, 1:经理, 2:员工
    
    # 关系
    user = db.relationship('User', backref='org_node')
    
    def to_dict(self):
        """转换为字典用于前端"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'full_name': self.user.full_name,
            'role': self.user.role.value,
            'title': self.user.title,
            'x': self.x,
            'y': self.y,
            'level': self.level,
            'workload_color': self.user.get_workload_color()
        }

class AIAnalysis(db.Model):
    """AI分析结果存储"""
    __tablename__ = 'ai_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 原始输入
    original_input = db.Column(db.Text, nullable=False)
    input_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # AI分析结果
    analyzed_title = db.Column(db.String(200))
    analyzed_description = db.Column(db.Text)
    estimated_hours = db.Column(db.Float)
    suggested_priority = db.Column(db.Enum(TaskPriority))
    
    # 拆解步骤 (存储为JSON)
    breakdown_steps = db.Column(db.Text)  # JSON格式: [{"step": "...", "hours": 2.5}, ...]
    
    # 元数据
    ai_model = db.Column(db.String(50))
    confidence_score = db.Column(db.Float)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    input_by = db.relationship('User', foreign_keys=[input_by_id])
    tasks = db.relationship('Task', backref='ai_analysis', lazy='dynamic')
    
    def get_steps(self):
        """获取拆解步骤列表"""
        if self.breakdown_steps:
            return json.loads(self.breakdown_steps)
        return []
    
    def get_step_count(self):
        """获取步骤数量"""
        return len(self.get_steps())

class Task(db.Model):
    """扩展的任务模型"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # 状态和优先级
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = db.Column(db.Enum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # 时间相关
    due_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float, default=0.0)
    
    # 分配相关
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ai_analysis_id = db.Column(db.Integer, db.ForeignKey('ai_analyses.id'))
    
    # 进度跟踪
    progress = db.Column(db.Integer, default=0)  # 0-100百分比
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    # 步骤跟踪 (对于AI拆解的任务)
    current_step = db.Column(db.Integer, default=0)
    total_steps = db.Column(db.Integer, default=1)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    updates = db.relationship('TaskUpdate', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_due_date_color(self):
        """根据截止时间获取颜色"""
        if not self.due_date:
            return 'secondary'
        
        days_left = (self.due_date - datetime.utcnow()).days
        
        if days_left < 0:
            return 'danger'      # 红色 - 已过期
        elif days_left == 0:
            return 'warning'     # 黄色 - 今天到期
        elif days_left <= 2:
            return 'warning'     # 黄色 - 2天内到期
        elif days_left <= 7:
            return 'info'        # 蓝色 - 一周内到期
        else:
            return 'success'     # 绿色 - 时间充足
    
    def get_priority_color(self):
        """获取优先级颜色"""
        return {
            TaskPriority.URGENT: 'danger',
            TaskPriority.HIGH: 'warning',
            TaskPriority.MEDIUM: 'info',
            TaskPriority.LOW: 'success'
        }.get(self.priority, 'secondary')
    
    def get_time_view(self):
        """获取时间视图分类"""
        if not self.due_date:
            return 'month'  # 无截止日期归为月度视图
        
        days_left = (self.due_date - datetime.utcnow()).days
        
        if days_left == 0:
            return 'today'
        elif days_left <= 7:
            return 'week'
        else:
            return 'month'

class TaskUpdate(db.Model):
    """任务更新记录"""
    __tablename__ = 'task_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 更新内容
    old_status = db.Column(db.Enum(TaskStatus))
    new_status = db.Column(db.Enum(TaskStatus))
    old_progress = db.Column(db.Integer)
    new_progress = db.Column(db.Integer)
    notes = db.Column(db.Text)
    
    # 如果是步骤完成
    completed_step = db.Column(db.Integer)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='task_updates')

class Reminder(db.Model):
    """提醒系统"""
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 提醒目标
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    
    # 提醒内容
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    reminder_type = db.Column(db.String(50))  # report_due, task_due, check_in, manual
    
    # 时间控制
    scheduled_time = db.Column(db.DateTime, nullable=False)
    sent_time = db.Column(db.DateTime)
    is_sent = db.Column(db.Boolean, default=False)
    
    # 重复设置
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(50))  # daily, weekly, monthly
    
    # 关系
    user = db.relationship('User', backref='reminders')
    task = db.relationship('Task', backref='reminders')
    
    def should_send_now(self):
        """检查是否应该发送提醒"""
        if self.is_sent:
            return False
        
        now = datetime.utcnow()
        return now >= self.scheduled_time

class WorkloadSnapshot(db.Model):
    """工作负载快照 - 用于历史分析"""
    __tablename__ = 'workload_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 负载数据
    task_count = db.Column(db.Integer, default=0)
    workload_percentage = db.Column(db.Float, default=0.0)
    completed_today = db.Column(db.Integer, default=0)
    
    # 时间戳
    snapshot_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='workload_snapshots')