from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page."""
    return render_template('index.html', 
                         app_name=current_app.config['APP_NAME'],
                         app_version=current_app.config['APP_VERSION'])

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    # Get user's tasks
    pending_tasks = current_user.tasks_assigned.filter_by(status='pending').all()
    in_progress_tasks = current_user.tasks_assigned.filter_by(status='in_progress').all()
    
    # Get recent notifications
    notifications = current_user.notifications.filter_by(is_read=False).order_by(
        Notification.created_at.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html',
                         pending_tasks=pending_tasks,
                         in_progress_tasks=in_progress_tasks,
                         notifications=notifications)

@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@main_bp.route('/help')
def help():
    """Help documentation."""
    return render_template('help.html')