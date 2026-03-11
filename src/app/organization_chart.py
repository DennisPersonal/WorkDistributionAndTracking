"""组织架构图模块 - 支持可视化、拖拽编辑"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from src.app import db
from src.app.models_extended import User, UserRole, OrganizationNode

class ChartLayout(Enum):
    """图表布局类型"""
    HIERARCHICAL = "hierarchical"  # 层级布局
    TREE = "tree"                  # 树状布局
    FORCE = "force"                # 力导向布局

@dataclass
class NodePosition:
    """节点位置信息"""
    node_id: int
    user_id: int
    x: float
    y: float
    level: int
    username: str
    full_name: str
    role: str
    title: str
    workload_color: str

class OrganizationChart:
    """组织架构图管理器"""
    
    def __init__(self, layout: ChartLayout = ChartLayout.HIERARCHICAL):
        self.layout = layout
        self.node_spacing_x = 200  # 节点水平间距
        self.node_spacing_y = 150  # 节点垂直间距
        self.level_height = 200    # 每层高度
    
    def generate_chart_data(self, director_id: Optional[int] = None) -> Dict[str, Any]:
        """
        生成组织架构图数据
        
        Args:
            director_id: 总监ID，如果为None则查找第一个总监
            
        Returns:
            包含节点和边的数据
        """
        # 查找或创建总监
        if director_id:
            director = User.query.get(director_id)
        else:
            director = User.query.filter_by(role=UserRole.DIRECTOR).first()
            
            # 如果没有总监，创建一个
            if not director:
                director = self._create_default_organization()
        
        # 获取所有用户并创建/更新节点
        all_users = User.query.filter_by(is_active=True).all()
        nodes = []
        
        for user in all_users:
            node = self._get_or_create_node(user)
            nodes.append(node)
        
        # 生成边（汇报关系）
        edges = self._generate_edges(all_users)
        
        # 应用布局
        positioned_nodes = self._apply_layout(nodes, director.id)
        
        return {
            "nodes": [node.to_dict() for node in positioned_nodes],
            "edges": edges,
            "layout": self.layout.value,
            "director_id": director.id,
            "director_name": director.full_name or director.username
        }
    
    def _create_default_organization(self) -> User:
        """创建默认的组织架构（1总监，4经理，40员工）"""
        import random
        from faker import Faker
        fake = Faker()
        
        # 创建总监
        director = User(
            username="director",
            email="director@company.com",
            full_name="张总监",
            role=UserRole.DIRECTOR,
            title="技术总监",
            department="技术部"
        )
        director.set_password("director123")
        db.session.add(director)
        db.session.commit()
        
        # 创建4个经理
        managers = []
        manager_names = ["王经理", "李经理", "赵经理", "刘经理"]
        
        for i, name in enumerate(manager_names, 1):
            manager = User(
                username=f"manager{i}",
                email=f"manager{i}@company.com",
                full_name=name,
                role=UserRole.MANAGER,
                title="项目经理",
                department="技术部",
                reports_to_id=director.id
            )
            manager.set_password(f"manager{i}123")
            managers.append(manager)
            db.session.add(manager)
        
        db.session.commit()
        
        # 创建40个员工（每个经理10个）
        employee_counter = 1
        for manager in managers:
            for j in range(1, 11):
                employee = User(
                    username=f"employee{employee_counter}",
                    email=f"employee{employee_counter}@company.com",
                    full_name=fake.name(),
                    role=UserRole.EMPLOYEE,
                    title="软件工程师",
                    department="技术部",
                    reports_to_id=manager.id
                )
                employee.set_password(f"employee{employee_counter}123")
                db.session.add(employee)
                employee_counter += 1
        
        db.session.commit()
        return director
    
    def _get_or_create_node(self, user: User) -> OrganizationNode:
        """获取或创建组织节点"""
        node = OrganizationNode.query.filter_by(user_id=user.id).first()
        
        if not node:
            # 确定层级
            if user.role == UserRole.DIRECTOR:
                level = 0
            elif user.role == UserRole.MANAGER:
                level = 1
            else:
                level = 2
            
            # 创建新节点
            node = OrganizationNode(
                user_id=user.id,
                level=level,
                x=0.0,
                y=0.0
            )
            db.session.add(node)
            db.session.commit()
        
        return node
    
    def _generate_edges(self, users: List[User]) -> List[Dict[str, Any]]:
        """生成边（汇报关系）"""
        edges = []
        
        for user in users:
            if user.reports_to_id:
                # 查找汇报上级的节点
                from_node = OrganizationNode.query.filter_by(user_id=user.id).first()
                to_node = OrganizationNode.query.filter_by(user_id=user.reports_to_id).first()
                
                if from_node and to_node:
                    edges.append({
                        "from": from_node.id,
                        "to": to_node.id,
                        "type": "reports_to",
                        "label": f"{user.full_name} → {user.reports_to.full_name}"
                    })
        
        return edges
    
    def _apply_layout(self, nodes: List[OrganizationNode], director_id: int) -> List[OrganizationNode]:
        """应用布局算法，计算节点位置"""
        
        # 按层级分组
        nodes_by_level = {0: [], 1: [], 2: []}
        for node in nodes:
            if node.level in nodes_by_level:
                nodes_by_level[node.level].append(node)
        
        # 计算位置
        if self.layout == ChartLayout.HIERARCHICAL:
            return self._hierarchical_layout(nodes_by_level, director_id)
        elif self.layout == ChartLayout.TREE:
            return self._tree_layout(nodes_by_level, director_id)
        else:  # FORCE
            return self._force_layout(nodes, director_id)
    
    def _hierarchical_layout(self, nodes_by_level: Dict[int, List[OrganizationNode]], director_id: int) -> List[OrganizationNode]:
        """层级布局"""
        positioned_nodes = []
        
        # 总监层（第0层）
        level0_nodes = nodes_by_level.get(0, [])
        start_x = - (len(level0_nodes) - 1) * self.node_spacing_x / 2
        
        for i, node in enumerate(level0_nodes):
            node.x = start_x + i * self.node_spacing_x
            node.y = 0
            positioned_nodes.append(node)
        
        # 经理层（第1层）
        level1_nodes = nodes_by_level.get(1, [])
        if level1_nodes:
            start_x = - (len(level1_nodes) - 1) * self.node_spacing_x / 2
            
            for i, node in enumerate(level1_nodes):
                node.x = start_x + i * self.node_spacing_x
                node.y = self.level_height
                positioned_nodes.append(node)
        
        # 员工层（第2层）
        level2_nodes = nodes_by_level.get(2, [])
        if level2_nodes:
            # 按经理分组员工
            employees_by_manager = {}
            for node in level2_nodes:
                user = User.query.get(node.user_id)
                if user and user.reports_to_id:
                    if user.reports_to_id not in employees_by_manager:
                        employees_by_manager[user.reports_to_id] = []
                    employees_by_manager[user.reports_to_id].append(node)
            
            # 为每个经理的员工分配位置
            for manager_id, employees in employees_by_manager.items():
                manager_node = OrganizationNode.query.filter_by(user_id=manager_id).first()
                if manager_node:
                    start_x = manager_node.x - (len(employees) - 1) * self.node_spacing_x / 2
                    
                    for i, node in enumerate(employees):
                        node.x = start_x + i * self.node_spacing_x
                        node.y = self.level_height * 2
                        positioned_nodes.append(node)
        
        db.session.commit()
        return positioned_nodes
    
    def _tree_layout(self, nodes_by_level: Dict[int, List[OrganizationNode]], director_id: int) -> List[OrganizationNode]:
        """树状布局"""
        # 简化实现，使用层级布局
        return self._hierarchical_layout(nodes_by_level, director_id)
    
    def _force_layout(self, nodes: List[OrganizationNode], director_id: int) -> List[OrganizationNode]:
        """力导向布局（简化版）"""
        # 为每个节点分配随机初始位置
        import random
        
        for node in nodes:
            if node.x == 0 and node.y == 0:
                # 根据层级分配大致位置
                base_y = node.level * self.level_height
                node.x = random.uniform(-300, 300)
                node.y = base_y + random.uniform(-50, 50)
        
        db.session.commit()
        return nodes
    
    def update_node_position(self, node_id: int, x: float, y: float) -> bool:
        """更新节点位置（拖拽后）"""
        node = OrganizationNode.query.get(node_id)
        if not node:
            return False
        
        node.x = x
        node.y = y
        db.session.commit()
        return True
    
    def update_reporting_line(self, employee_id: int, new_manager_id: int) -> Dict[str, Any]:
        """更新汇报关系（拖拽改变上级）"""
        employee = User.query.get(employee_id)
        new_manager = User.query.get(new_manager_id)
        
        if not employee or not new_manager:
            return {"success": False, "error": "用户不存在"}
        
        if employee.role != UserRole.EMPLOYEE:
            return {"success": False, "error": "只能更改员工的汇报关系"}
        
        if new_manager.role != UserRole.MANAGER:
            return {"success": False, "error": "只能汇报给经理"}
        
        # 保存旧关系
        old_manager_id = employee.reports_to_id
        
        # 更新关系
        employee.reports_to_id = new_manager_id
        db.session.commit()
        
        # 重新计算布局
        self.generate_chart_data()
        
        return {
            "success": True,
            "employee_id": employee_id,
            "employee_name": employee.full_name,
            "old_manager_id": old_manager_id,
            "new_manager_id": new_manager_id,
            "new_manager_name": new_manager.full_name
        }
    
    def get_employee_view_data(self, employee_id: int) -> Dict[str, Any]:
        """获取员工视图的组织架构数据（只显示相关部分）"""
        employee = User.query.get(employee_id)
        if not employee:
            return {"error": "员工不存在"}
        
        # 获取员工的经理
        manager = None
        if employee.reports_to_id:
            manager = User.query.get(employee.reports_to_id)
        
        # 获取同组同事（同一个经理）
        colleagues = []
        if manager:
            colleagues = User.query.filter_by(
                reports_to_id=manager.id,
                is_active=True
            ).filter(User.id != employee_id).all()
        
        # 获取经理的同事（其他经理）
        peer_managers = []
        if manager and manager.reports_to_id:
            peer_managers = User.query.filter_by(
                reports_to_id=manager.reports_to_id,
                role=UserRole.MANAGER,
                is_active=True
            ).filter(User.id != manager.id).all()
        
        # 获取总监
        director = None
        if manager and manager.reports_to_id:
            director = User.query.get(manager.reports_to_id)
        
        # 组织数据
        nodes = []
        edges = []
        
        # 添加员工自己
        employee_node = self._get_or_create_node(employee)
        nodes.append(employee_node.to_dict())
        
        # 添加经理
        if manager:
            manager_node = self._get_or_create_node(manager)
            nodes.append(manager_node.to_dict())
            edges.append({
                "from": employee_node.id,
                "to": manager_node.id,
                "type": "reports_to"
            })
        
        # 添加同事
        for colleague in colleagues:
            colleague_node = self._get_or_create_node(colleague)
            nodes.append(colleague_node.to_dict())
        
        # 添加其他经理
        for peer in peer_managers:
            peer_node = self._get_or_create_node(peer)
            nodes.append(peer_node.to_dict())
        
        # 添加总监
        if director:
            director_node = self._get_or_create_node(director)
            nodes.append(director_node.to_dict())
            if manager:
                edges.append({
                    "from": manager_node.id,
                    "to": director_node.id,
                    "type": "reports_to"
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "employee": {
                "id": employee.id,
                "name": employee.full_name,
                "role": employee.role.value
            },
            "scope": "employee_view"
        }

# 全局实例
org_chart = OrganizationChart()