from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from src.app.models_extended import User

class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Registration form."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=128)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Validate username uniqueness."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        """Validate email uniqueness."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class TaskForm(FlaskForm):
    """Task creation/editing form."""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[Optional()], format='%Y-%m-%d')
    estimated_hours = FloatField('Estimated Hours', validators=[Optional()])
    submit = SubmitField('Save Task')


class TaskUpdateForm(FlaskForm):
    """Task update form."""
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    progress = SelectField('Progress', choices=[
        (0, '0%'),
        (25, '25%'),
        (50, '50%'),
        (75, '75%'),
        (100, '100%')
    ], coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    hours_spent = FloatField('Hours Spent', validators=[Optional()])
    submit = SubmitField('Update Task')


class ProjectForm(FlaskForm):
    """Project creation/editing form."""
    name = StringField('Project Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived')
    ], validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[Optional()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Save Project')


class ProfileForm(FlaskForm):
    """User profile editing form."""
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=128)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=8)])
    new_password2 = PasswordField('Repeat New Password', validators=[Optional(), EqualTo('new_password')])
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_email(self, email):
        """Validate email uniqueness (if changed)."""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')