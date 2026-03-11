from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from src.app import db
from src.app.models_extended import User
from src.app.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Account is disabled', 'warning')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        flash('Login successful!', 'success')
        
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile."""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile."""
    try:
        # 获取表单数据
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        title = request.form.get('title')
        department = request.form.get('department')
        weekly_capacity = request.form.get('weekly_capacity')
        active = request.form.get('active') == 'on'
        
        # 更新用户信息
        if full_name:
            current_user.full_name = full_name
        if email:
            current_user.email = email
        if title:
            current_user.title = title
        if department:
            current_user.department = department
        if weekly_capacity:
            try:
                current_user.weekly_capacity = int(weekly_capacity)
            except ValueError:
                pass
        current_user.active = active
        
        # 保存到数据库
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'danger')
    
    return redirect(url_for('auth.profile'))