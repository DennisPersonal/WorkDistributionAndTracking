from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name='default'):
    """Application factory function."""
    from src.config import config
    from src.app.models_extended import User
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Register blueprints
    from src.app.routes import main_bp
    from src.app.auth import auth_bp
    from src.app.ai_routes import ai_bp
    from src.app.org_routes import org_bp
    from src.app.task_routes import task_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(org_bp, url_prefix='/org')
    app.register_blueprint(task_bp, url_prefix='/tasks')
    
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app