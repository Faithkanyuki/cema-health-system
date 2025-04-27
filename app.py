from flask import Flask, request, jsonify
from models import db, HealthProgram, Client, ClientProgram
from datetime import datetime
import re
from functools import wraps  # Added for proper decorator handling

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['API_KEYS'] = {'default-key': 'admin'}  # Use environment variables in production
db.init_app(app)

# =========================
# Helper Functions
# =========================

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d').date()
        return True
    except ValueError:
        return False

def validate_name(name):
    return bool(re.match(r'^[a-zA-Z\s]{2,50}$', name))

def require_api_key(f):
    @wraps(f)  # This fixes the endpoint naming issue
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != app.config['API_KEYS']['default-key']:
            return jsonify({'error': 'Unauthorized', 'message': 'Valid API key required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# =========================
# Error Handlers
# =========================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error', 'message': 'Unexpected error occurred'}), 500

# =========================
# Health Program Endpoints
# =========================

@app.route('/')
def home():
    return jsonify({
        "message": "CEMA Health System API",
        "endpoints": {
            "programs": "/programs",
            "clients": "/clients",
            "client_profile": "/clients/<int:client_id>"
        }
    })



@app.route('/programs', methods=['POST'])
@require_api_key
def create_program():
    data = request.get_json()
    
    if not data.get('name') or not re.match(r'^[a-zA-Z0-9\s\-]{3,100}$', data['name']):
        return jsonify({'error': 'Validation Error', 'message': 'Program name is required and must be 3-100 chars'}), 400
    
    if HealthProgram.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Validation Error', 'message': 'Program already exists'}), 400

    new_program = HealthProgram(
        name=data['name'],
        description=data.get('description', '')[:200]
    )
    
    try:
        db.session.add(new_program)
        db.session.commit()
        return jsonify({"message": "Program created", "id": new_program.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database Error", "details": str(e)}), 500

@app.route('/programs', methods=['GET'])
def get_programs():
    programs = HealthProgram.query.all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description
    } for p in programs])

# =========================
# Client Endpoints
# =========================

@app.route('/clients', methods=['POST'])
@require_api_key
def register_client():
    data = request.get_json()
    
    if not all([data.get('first_name'), 
               data.get('last_name'), 
               data.get('date_of_birth')]):
        return jsonify({
            'error': 'Validation Error',
            'message': 'First name, last name, and date of birth are required'
        }), 400

    if not validate_date(data['date_of_birth']):
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid date format (YYYY-MM-DD required)'
        }), 400

    new_client = Client(
        first_name=data['first_name'].strip(),
        last_name=data['last_name'].strip(),
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
        contact_info=data.get('contact_info', '')[:100]
    )
    
    try:
        db.session.add(new_client)
        db.session.commit()
        return jsonify({
            "message": "Client registered",
            "id": new_client.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Database Error",
            "details": str(e)
        }), 500

@app.route('/clients', methods=['GET'])
def search_clients():
    search_term = request.args.get('q', '')
    if len(search_term) < 2:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Search term must be at least 2 characters'
        }), 400
    
    clients = Client.query.filter(
        (Client.first_name.ilike(f'%{search_term}%')) | 
        (Client.last_name.ilike(f'%{search_term}%'))
    ).limit(50).all()

    return jsonify([{
        "id": c.id,
        "name": f"{c.first_name} {c.last_name}",
        "dob": str(c.date_of_birth)
    } for c in clients])

@app.route('/clients/<int:client_id>', methods=['GET'])
def get_client_profile(client_id):
    client = Client.query.get_or_404(client_id)
    programs = ClientProgram.query.filter_by(client_id=client_id).join(HealthProgram).all()
    
    return jsonify({
        "id": client.id,
        "first_name": client.first_name,
        "last_name": client.last_name,
        "dob": str(client.date_of_birth),
        "contact_info": client.contact_info,
        "programs": [{
            "id": cp.program.id,
            "name": cp.program.name,
            "enrollment_date": str(cp.enrollment_date),
            "notes": cp.notes
        } for cp in programs]
    })

@app.route('/clients/<int:client_id>/programs', methods=['POST'])
@require_api_key
def enroll_client(client_id):
    data = request.get_json()
    
    if not data.get('program_id'):
        return jsonify({
            'error': 'Validation Error',
            'message': 'program_id is required'
        }), 400

    program = HealthProgram.query.get(data['program_id'])
    if not program:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Program not found'
        }), 404

    enrollment = ClientProgram(
        client_id=client_id,
        program_id=data['program_id'],
        enrollment_date=datetime.now().date(),
        notes=data.get('notes', '')[:500]
    )

    try:
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({
            "message": "Client enrolled in program",
            "program": program.name
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Database Error",
            "details": str(e)
        }), 500

# =========================
# Main Application
# =========================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)