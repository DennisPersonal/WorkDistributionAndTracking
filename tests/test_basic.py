"""Basic tests for the Flask application."""

import pytest
from src.app import create_app, db
from src.app.models import User


@pytest.fixture
def app():
    """Create test application."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI runner."""
    return app.test_cli_runner()


def test_app_creation(app):
    """Test that the app is created correctly."""
    assert app is not None
    assert app.config['TESTING'] is True


def test_home_page(client):
    """Test home page accessibility."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Work Distribution' in response.data


def test_database_connection(app):
    """Test database connection and model creation."""
    with app.app_context():
        # Create a test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Retrieve the user
        retrieved_user = User.query.filter_by(username='testuser').first()
        assert retrieved_user is not None
        assert retrieved_user.email == 'test@example.com'
        assert retrieved_user.check_password('password123')


def test_login_page(client):
    """Test login page accessibility."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data or b'Sign In' in response.data


def test_register_page(client):
    """Test registration page accessibility."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data


def test_about_page(client):
    """Test about page accessibility."""
    response = client.get('/about')
    assert response.status_code == 200


def test_help_page(client):
    """Test help page accessibility."""
    response = client.get('/help')
    assert response.status_code == 200