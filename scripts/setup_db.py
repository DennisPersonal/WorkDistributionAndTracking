#!/usr/bin/env python3
"""Initialize the database with sample data."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import create_app, db
from src.app.models import User, Task, Project, TaskUpdate, Notification
from datetime import datetime, timedelta

def create_sample_data():
    """Create sample data for development."""
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("Creating sample data...")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            full_name='Administrator',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create regular users
        users = []
        for i in range(1, 4):
            user = User(
                username=f'user{i}',
                email=f'user{i}@example.com',
                full_name=f'User {i}',
                role='user'
            )
            user.set_password(f'user{i}123')
            users.append(user)
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users) + 1} users")
        
        # Create projects
        projects = []
        project_names = ['Website Redesign', 'Mobile App Development', 'Marketing Campaign']
        
        for i, name in enumerate(project_names):
            project = Project(
                name=name,
                description=f'Description for {name} project',
                status='active',
                start_date=datetime.utcnow() - timedelta(days=30),
                end_date=datetime.utcnow() + timedelta(days=30)
            )
            projects.append(project)
            db.session.add(project)
        
        db.session.commit()
        print(f"Created {len(projects)} projects")
        
        # Create tasks
        tasks = []
        task_templates = [
            ('Design homepage layout', 'pending', 'high', 8.0),
            ('Implement user authentication', 'in_progress', 'high', 16.0),
            ('Write API documentation', 'pending', 'medium', 4.0),
            ('Fix login bug', 'completed', 'urgent', 2.0),
            ('Add dark mode', 'pending', 'low', 12.0),
            ('Optimize database queries', 'in_progress', 'medium', 8.0),
            ('Update dependencies', 'pending', 'medium', 4.0),
            ('Write unit tests', 'pending', 'high', 10.0),
        ]
        
        for i, (title, status, priority, hours) in enumerate(task_templates):
            task = Task(
                title=title,
                description=f'Description for {title}',
                status=status,
                priority=priority,
                due_date=datetime.utcnow() + timedelta(days=i+7),
                estimated_hours=hours,
                assigned_to_id=users[i % len(users)].id,
                created_by_id=admin.id,
                project_id=projects[i % len(projects)].id
            )
            tasks.append(task)
            db.session.add(task)
        
        db.session.commit()
        print(f"Created {len(tasks)} tasks")
        
        # Create task updates
        for i, task in enumerate(tasks[:4]):
            update = TaskUpdate(
                task_id=task.id,
                user_id=task.assigned_to_id,
                status=task.status,
                progress=25 * (i + 1),
                notes=f'Update for {task.title}',
                hours_spent=task.estimated_hours * 0.5
            )
            db.session.add(update)
        
        db.session.commit()
        print("Created task updates")
        
        # Create notifications
        for user in [admin] + users:
            notification = Notification(
                user_id=user.id,
                title='Welcome to Work Distribution System',
                message='Thank you for joining our platform!',
                type='info',
                is_read=False
            )
            db.session.add(notification)
        
        db.session.commit()
        print("Created notifications")
        
        print("\nSample data created successfully!")
        print("\nLogin credentials:")
        print("Admin: username='admin', password='admin123'")
        for i, user in enumerate(users, 1):
            print(f"User {i}: username='{user.username}', password='{user.username}123'")

if __name__ == '__main__':
    create_sample_data()