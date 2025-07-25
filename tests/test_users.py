import pytest
from app import create_app, db
from models import User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_user(client):
    response = client.post('/users/', json={
        "name": "Test User",
        "email": "test@example.com",
        "address": "123 Test St"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == "Test User"
    assert data['email'] == "test@example.com"
