"""AI集成模块 - 任务分析和智能分配"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
# openai 是可选的，只在需要时导入
from src.app import db
from src.app.models_extended import User, Task, AIAnalysis, TaskPriority, UserRole

class AIModelType(Enum):
    """AI模型类型"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    LOCAL = "local"
    MOCK = "mock"  # 模拟模式，用于开发测试

class TaskAnalyzer:
    """任务分析器 - 将老板输入转换为结构化任务"""
    
    def __init__(self, model_type: AIModelType = AIModelType.MOCK):
        self.model_type = model_type
        self.setup_model()
    
    def setup_model(self):
        """设置AI模型"""
        if self.model_type == AIModelType.OPENAI:
            # 从环境变量获取OpenAI API密钥
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY环境变量未设置")
            openai.api_key = api_key
        elif self.model_type == AIModelType.LOCAL:
            # 设置本地模型
            # 这里可以集成本地LLM如Llama、ChatGLM等
            pass
    
    def analyze_task(self, user_input: str, user_id: int) -> Dict[str, Any]:
        """
        分析任务输入，返回结构化结果
        
        Args:
            user_input: 用户输入的自然语言描述
            user_id: 输入用户的ID
            
        Returns:
            包含分析结果的字典
        """
        if self.model_type == AIModelType.MOCK:
            return self._mock_analysis(user_input, user_id)
        elif self.model_type == AIModelType.OPENAI:
            return self._openai_analysis(user_input, user_id)
        elif self.model_type == AIModelType.DEEPSEEK:
            return self._deepseek_analysis(user_input, user_id)
        elif self.model_type == AIModelType.LOCAL:
            return self._local_analysis(user_input, user_id)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
    
    def _mock_analysis(self, user_input: str, user_id: int) -> Dict[str, Any]:
        """模拟分析 - 用于开发和测试"""
        # 简单的关键词匹配来模拟AI分析
        input_lower = user_input.lower()
        
        # 分析优先级
        if any(word in input_lower for word in ['紧急', '立刻', '马上', 'urgent', 'asap']):
            priority = TaskPriority.URGENT
        elif any(word in input_lower for word in ['重要', '优先', 'high', 'important']):
            priority = TaskPriority.HIGH
        elif any(word in input_lower for word in ['一般', '中等', 'medium']):
            priority = TaskPriority.MEDIUM
        else:
            priority = TaskPriority.LOW
        
        # 分析预估时间
        if '复杂' in input_lower or '困难' in input_lower:
            estimated_hours = 16.0
            steps = 8
        elif '中等' in input_lower:
            estimated_hours = 8.0
            steps = 4
        else:
            estimated_hours = 4.0
            steps = 2
        
        # 分析任务类型和分配
        tasks = []
        
        # 检查是否包含具体人员分配
        if 'john' in input_lower or 'employee1' in input_lower:
            tasks.append({
                "title": "John的任务",
                "description": user_input,
                "assigned_to": "employee1",
                "estimated_hours": estimated_hours / 2,
                "priority": priority,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat()
            })
        
        if 'sarah' in input_lower or 'employee2' in input_lower:
            tasks.append({
                "title": "Sarah的任务",
                "description": user_input,
                "assigned_to": "employee2",
                "estimated_hours": estimated_hours / 2,
                "priority": priority,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat()
            })
        
        if 'mike' in input_lower or 'employee3' in input_lower:
            tasks.append({
                "title": "Mike的任务",
                "description": user_input,
                "assigned_to": "employee3",
                "estimated_hours": estimated_hours / 2,
                "priority": priority,
                "due_date": (datetime.now() + timedelta(days=7)).isoformat()
            })
        
        # 如果没有具体人员，创建通用任务
        if not tasks:
            tasks.append({
                "title": f"任务: {user_input[:30]}...",
                "description": user_input,
                "assigned_to": None,
                "estimated_hours": estimated_hours,
                "priority": priority,
                "due_date": (datetime.now() + timedelta(days=14)).isoformat()
            })
        
        # 生成步骤
        breakdown_steps = []
        for i in range(steps):
            step_hours = estimated_hours / steps
            breakdown_steps.append({
                "step": f"步骤 {i+1}: 完成相关子任务",
                "estimated_hours": step_hours,
                "description": f"这是第{i+1}个步骤，需要约{step_hours}小时完成"
            })
        
        return {
            "analyzed_title": f"分析任务: {user_input[:50]}...",
            "analyzed_description": f"基于您的输入'{user_input}'，已分析并拆解为{steps}个步骤。",
            "estimated_hours": estimated_hours,
            "suggested_priority": priority,
            "breakdown_steps": breakdown_steps,
            "tasks": tasks,
            "confidence_score": 0.85,
            "ai_model": "mock_model_v1"
        }
    
    def _openai_analysis(self, user_input: str, user_id: int) -> Dict[str, Any]:
        """使用OpenAI API进行分析"""
        try:
            import openai
            
            prompt = f"""
            请分析以下工作任务描述，并拆解为可执行的步骤：
            
            原始描述：{user_input}
            
            请以JSON格式返回分析结果，包含以下字段：
            1. title: 任务标题（简洁明了）
            2. description: 任务详细描述
            3. estimated_hours: 预估总工时（小时）
            4. priority: 优先级（urgent/high/medium/low）
            5. steps: 拆解步骤列表，每个步骤包含：
               - step: 步骤描述
               - estimated_hours: 该步骤预估工时
               - description: 步骤详细说明
            
            示例格式：
            {{
                "title": "网站首页 redesign",
                "description": "重新设计公司网站首页，提升用户体验",
                "estimated_hours": 24.5,
                "priority": "high",
                "steps": [
                    {{
                        "step": "需求分析和竞品调研",
                        "estimated_hours": 4.0,
                        "description": "收集需求，分析竞品网站设计"
                    }}
                ]
            }}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的项目任务分析助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            # 转换优先级枚举
            priority_map = {
                'urgent': TaskPriority.URGENT,
                'high': TaskPriority.HIGH,
                'medium': TaskPriority.MEDIUM,
                'low': TaskPriority.LOW
            }
            
            return {
                "analyzed_title": result.get("title", ""),
                "analyzed_description": result.get("description", ""),
                "estimated_hours": float(result.get("estimated_hours", 8.0)),
                "suggested_priority": priority_map.get(result.get("priority", "medium"), TaskPriority.MEDIUM),
                "breakdown_steps": result.get("steps", []),
                "confidence_score": 0.9,
                "ai_model": "gpt-3.5-turbo"
            }
            
        except ImportError:
            print("OpenAI库未安装，使用模拟分析")
            return self._mock_analysis(user_input, user_id)
        except Exception as e:
            # 如果OpenAI失败，回退到模拟分析
            print(f"OpenAI分析失败: {e}")
            return self._mock_analysis(user_input, user_id)
    
    def _deepseek_analysis(self, user_input: str, user_id: int) -> Dict[str, Any]:
        """使用DeepSeek API进行分析"""
        try:
            import requests
            import json
            
            # 从环境变量获取DeepSeek API密钥
            api_key = os.environ.get('DEEPSEEK_API_KEY')
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY环境变量未设置")
            
            prompt = f"""
            请分析以下工作任务描述，并拆解为可执行的步骤：
            
            原始描述：{user_input}
            
            请以JSON格式返回分析结果，包含以下字段：
            1. title: 任务标题（简洁明了）
            2. description: 任务详细描述
            3. estimated_hours: 预估总工时（小时）
            4. priority: 优先级（urgent/high/medium/low）
            5. steps: 拆解步骤列表，每个步骤包含：
               - step: 步骤描述
               - estimated_hours: 该步骤预估工时
               - description: 步骤详细说明
            
            示例格式：
            {{
                "title": "网站首页 redesign",
                "description": "重新设计公司网站首页，提升用户体验",
                "estimated_hours": 24.5,
                "priority": "high",
                "steps": [
                    {{
                        "step": "需求分析和竞品调研",
                        "estimated_hours": 4.0,
                        "description": "收集需求，分析竞品网站设计"
                    }}
                ]
            }}
            
            请确保返回纯JSON格式，不要包含其他文本。
            """
            
            # 调用DeepSeek API
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个专业的项目任务分析助手。请严格按照要求的JSON格式返回分析结果。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"DeepSeek API错误: {response.status_code} - {response.text}")
            
            result_data = response.json()
            result_text = result_data["choices"][0]["message"]["content"]
            
            # 清理响应文本，提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group()
            
            result = json.loads(result_text)
            
            # 转换优先级枚举
            priority_map = {
                'urgent': TaskPriority.URGENT,
                'high': TaskPriority.HIGH,
                'medium': TaskPriority.MEDIUM,
                'low': TaskPriority.LOW
            }
            
            return {
                "analyzed_title": result.get("title", ""),
                "analyzed_description": result.get("description", ""),
                "estimated_hours": float(result.get("estimated_hours", 8.0)),
                "suggested_priority": priority_map.get(result.get("priority", "medium"), TaskPriority.MEDIUM),
                "breakdown_steps": result.get("steps", []),
                "confidence_score": 0.9,
                "ai_model": "deepseek-chat"
            }
            
        except Exception as e:
            # 如果DeepSeek失败，回退到模拟分析
            print(f"DeepSeek分析失败: {e}")
            return self._mock_analysis(user_input, user_id)
    
    def _local_analysis(self, user_input: str, user_id: int) -> Dict[str, Any]:
        """使用本地模型进行分析"""
        # 这里可以集成本地LLM
        # 暂时回退到模拟分析
        return self._mock_analysis(user_input, user_id)
    
    def save_analysis(self, user_input: str, user_id: int, analysis_result: Dict[str, Any]) -> AIAnalysis:
        """保存分析结果到数据库"""
        
        analysis = AIAnalysis(
            original_input=user_input,
            input_by_id=user_id,
            analyzed_title=analysis_result.get("analyzed_title", ""),
            analyzed_description=analysis_result.get("analyzed_description", ""),
            estimated_hours=analysis_result.get("estimated_hours", 8.0),
            suggested_priority=analysis_result.get("suggested_priority", TaskPriority.MEDIUM),
            breakdown_steps=json.dumps(analysis_result.get("breakdown_steps", []), ensure_ascii=False),
            ai_model=analysis_result.get("ai_model", "unknown"),
            confidence_score=analysis_result.get("confidence_score", 0.0)
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return analysis

class TaskAllocator:
    """任务分配器 - 智能分配任务给员工"""
    
    def __init__(self):
        self.min_tasks_per_employee = 1  # 每个员工最少分配任务数
        self.max_workload_percentage = 80  # 最大工作负载百分比
    
    def allocate_tasks(self, analysis_id: int, manager_id: int) -> Dict[str, Any]:
        """
        根据AI分析结果分配任务
        
        Args:
            analysis_id: AI分析记录的ID
            manager_id: 分配任务的经理ID
            
        Returns:
            分配结果
        """
        # 获取分析结果
        analysis = AIAnalysis.query.get(analysis_id)
        if not analysis:
            raise ValueError(f"未找到分析记录: {analysis_id}")
        
        # 获取经理的下属员工
        manager = User.query.get(manager_id)
        if not manager or manager.role != UserRole.MANAGER:
            raise ValueError(f"用户不是经理或不存在: {manager_id}")
        
        employees = User.query.filter_by(
            reports_to_id=manager_id,
            role=UserRole.EMPLOYEE,
            is_active=True
        ).all()
        
        if not employees:
            raise ValueError(f"经理 {manager_id} 没有下属员工")
        
        # 获取拆解步骤
        steps = analysis.get_steps()
        step_count = len(steps)
        
        if step_count == 0:
            # 如果没有拆解步骤，创建一个总任务
            return self._allocate_single_task(analysis, manager, employees)
        else:
            # 根据步骤数量分配
            return self._allocate_by_steps(analysis, steps, manager, employees)
    
    def _allocate_single_task(self, analysis: AIAnalysis, manager: User, employees: List[User]) -> Dict[str, Any]:
        """分配单个任务（无拆解步骤）"""
        # 选择工作负载最低的员工
        employees_sorted = sorted(employees, key=lambda e: e.current_workload)
        selected_employee = employees_sorted[0]
        
        # 创建任务
        task = Task(
            title=analysis.analyzed_title,
            description=analysis.analyzed_description,
            priority=analysis.suggested_priority,
            estimated_hours=analysis.estimated_hours,
            created_by_id=manager.id,
            assigned_to_id=selected_employee.id,
            ai_analysis_id=analysis.id,
            total_steps=1,
            due_date=datetime.utcnow() + timedelta(days=7)  # 默认一周后截止
        )
        
        db.session.add(task)
        
        # 更新员工工作负载
        self._update_employee_workload(selected_employee, analysis.estimated_hours)
        
        db.session.commit()
        
        return {
            "success": True,
            "allocated_tasks": 1,
            "employee_count": 1,
            "details": [{
                "task_id": task.id,
                "employee_id": selected_employee.id,
                "employee_name": selected_employee.full_name,
                "task_title": task.title
            }]
        }
    
    def _allocate_by_steps(self, analysis: AIAnalysis, steps: List[Dict], manager: User, employees: List[User]) -> Dict[str, Any]:
        """根据步骤数量分配任务"""
        step_count = len(steps)
        employee_count = len(employees)
        
        # 计算每个员工应该分配的任务数
        tasks_per_employee = max(self.min_tasks_per_employee, step_count // employee_count)
        
        # 如果步骤数少于员工数，调整
        if step_count < employee_count:
            tasks_per_employee = 1
            # 只选择部分员工
            employees = employees[:step_count]
        
        allocation_result = {
            "success": True,
            "total_steps": step_count,
            "employee_count": len(employees),
            "tasks_per_employee": tasks_per_employee,
            "details": []
        }
        
        # 按工作负载排序员工
        employees_sorted = sorted(employees, key=lambda e: e.current_workload)
        
        step_index = 0
        for employee in employees_sorted:
            # 为每个员工分配 tasks_per_employee 个步骤
            for i in range(tasks_per_employee):
                if step_index >= step_count:
                    break
                
                step = steps[step_index]
                
                # 创建任务（每个步骤作为一个任务）
                task = Task(
                    title=f"{analysis.analyzed_title} - 步骤{step_index + 1}",
                    description=f"{step.get('description', '')}\n\n原任务: {analysis.analyzed_description}",
                    priority=analysis.suggested_priority,
                    estimated_hours=step.get('estimated_hours', analysis.estimated_hours / step_count),
                    created_by_id=manager.id,
                    assigned_to_id=employee.id,
                    ai_analysis_id=analysis.id,
                    current_step=step_index + 1,
                    total_steps=step_count,
                    due_date=datetime.utcnow() + timedelta(days=7)  # 默认一周后截止
                )
                
                db.session.add(task)
                
                # 记录分配详情
                allocation_result["details"].append({
                    "task_id": task.id,
                    "employee_id": employee.id,
                    "employee_name": employee.full_name,
                    "step_number": step_index + 1,
                    "step_description": step.get('step', ''),
                    "estimated_hours": task.estimated_hours
                })
                
                # 更新员工工作负载
                self._update_employee_workload(employee, task.estimated_hours)
                
                step_index += 1
        
        db.session.commit()
        return allocation_result
    
    def _update_employee_workload(self, employee: User, additional_hours: float):
        """更新员工工作负载"""
        # 这里简化计算：假设每周40工作小时
        weekly_hours = 40
        
        # 计算新增工作负载百分比
        additional_load = (additional_hours / weekly_hours) * 100
        
        # 更新工作负载
        employee.current_workload = min(
            self.max_workload_percentage,
            employee.current_workload + additional_load
        )
        employee.current_task_count += 1
        
        # 创建工作负载快照
        from src.app.models_extended import WorkloadSnapshot
        snapshot = WorkloadSnapshot(
            user_id=employee.id,
            task_count=employee.current_task_count,
            workload_percentage=employee.current_workload
        )
        db.session.add(snapshot)

class ReminderScheduler:
    """提醒调度器"""
    
    def check_and_send_reminders(self):
        """检查并发送到期提醒"""
        from src.app.models_extended import Reminder
        
        now = datetime.utcnow()
        due_reminders = Reminder.query.filter(
            Reminder.scheduled_time <= now,
            Reminder.is_sent == False
        ).all()
        
        sent_count = 0
        for reminder in due_reminders:
            if self._send_reminder(reminder):
                reminder.is_sent = True
                reminder.sent_time = now
                sent_count += 1
        
        if sent_count > 0:
            db.session.commit()
        
        return sent_count
    
    def _send_reminder(self, reminder: Reminder) -> bool:
        """发送单个提醒"""
        # 这里可以实现实际的发送逻辑
        # 例如：发送站内消息、邮件、Slack通知等
        
        # 目前只是记录日志
        print(f"发送提醒: {reminder.title} 给用户 {reminder.user_id}")
        
        # 创建通知记录
        from src.app.models_extended import Notification
        notification = Notification(
            user_id=reminder.user_id,
            title=reminder.title,
            message=reminder.message,
            type="reminder",
            link=f"/tasks/{reminder.task_id}" if reminder.task_id else None
        )
        db.session.add(notification)
        
        return True
    
    def schedule_task_reminders(self, task: Task):
        """为任务安排提醒"""
        if not task.due_date:
            return
        
        # 提前1天提醒
        reminder_time = task.due_date - timedelta(days=1)
        
        reminder = Reminder(
            user_id=task.assigned_to_id,
            task_id=task.id,
            title=f"任务即将到期: {task.title}",
            message=f"您的任务 '{task.title}' 将于 {task.due_date.strftime('%Y-%m-%d')} 到期，请及时完成。",
            reminder_type="task_due",
            scheduled_time=reminder_time
        )
        
        db.session.add(reminder)
        db.session.commit()

# 全局实例
task_analyzer = TaskAnalyzer()
task_allocator = TaskAllocator()
reminder_scheduler = ReminderScheduler()