"""Pytest fixtures for the Flask API tests."""
import pytest

from app import create_app
from app.extensions import db as _db
from app.models.user import Organization, User


@pytest.fixture(scope='session')
def app():
    """Create the Flask app with test config."""
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """Provide a clean database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client, db):
    """Register a user and return auth headers."""
    resp = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
        'organization_name': 'Test University',
    })
    data = resp.get_json()
    token = data['access_token']
    return {'Authorization': f'Bearer {token}'}
