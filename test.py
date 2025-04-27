import pytest
from app import app, db
from models import HealthProgram, Client, ClientProgram
import json
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_program(client):
    response = client.post('/programs', json={
        'name': 'HIV',
        'description': 'HIV Treatment Program'
    })
    assert response.status_code == 201
    assert 'id' in response.json

def test_register_client(client):
    response = client.post('/clients', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'date_of_birth': '1990-01-01',
        'contact_info': 'john@example.com'
    })
    assert response.status_code == 201
    assert 'id' in response.json

def test_client_profile(client):
    # Create test data
    client_obj = Client(
        first_name='Jane',
        last_name='Smith',
        date_of_birth=datetime.strptime('1985-05-15', '%Y-%m-%d').date(),
        contact_info='jane@example.com'
    )
    program = HealthProgram(name='Malaria', description='Malaria Prevention')
    db.session.add_all([client_obj, program])
    db.session.commit()
    
    # Enroll client
    enrollment = ClientProgram(
        client_id=client_obj.id,
        program_id=program.id,
        enrollment_date=datetime.now().date()
    )
    db.session.add(enrollment)
    db.session.commit()
    
    # Test API
    response = client.get(f'/clients/{client_obj.id}')
    assert response.status_code == 200
    data = response.json
    assert data['first_name'] == 'Jane'
    assert len(data['programs']) == 1
    assert data['programs'][0]['name'] == 'Malaria'