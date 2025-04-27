from flask import Flask, request, jsonify
from models import db, HealthProgram, Client, ClientProgram
from datetime import datetime
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['API_KEYS'] = {'default-key': 'admin'}  # Use environment variables in production
db.init_app(app)

# =========================
# Helper Functions
# =========================

# Validate Date
def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d').date()  # Check if the date is valid
        return True
    except ValueError:
        return False

# Validate Name (only letters and spaces, 2-50 chars)
def validate_name(name):
    return bool(re.match(r'^[a-zA-Z\s]{2,50}$', name))

# Simple API key validation (decorator)
def require_api_key(f):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != app.config['API_KEYS']['default-key']:
            return jsonify({'error': 'Unauthorized', 'message': 'Valid API key required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# =========================
# Error Handlers
# =========================

# Handle 400 Bad Request errors
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

# Handle 404 Not Found errors
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': 'Resource not found'}), 404

# Handle 500 Internal Server errors
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error', 'message': 'Unexpected error occurred'}), 500

# =========================
# Health Program Endpoints
# =========================

# Create a new health program
@app.route('/programs', methods=['POST'])
@require_api_key
def create_program():
    data = request.get_json()
    
    # Validate program name
    if not data.get('name') or not re.match(r'^[a-zA-Z0-9\s\-]{3,100}$', data['name']):
        return jsonify({'error': 'Validation Error', 'message': 'Program name is required and must be 3-100 chars'}), 400
    
    if HealthProgram.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Validation Error', 'message': 'Program already exists'}), 400

    # Create and save program
    new_program = HealthProgram(name=data['name'], description=data.get('description', '')[:200])
    try:
        db.session.add(new_program)
        db.session.commit()
        return jsonify({"message": "Program created", "id": new_program.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database Error"}), 500

# Get all programs
@app.route('/programs', methods=['GET'])
def get_programs():
    programs = HealthProgram.query.all()
    return jsonify([{"id": p.id, "name": p.name} for p in programs])

# =========================
# Client Endpoints
# =========================

# Register a new client
@app.route('/clients', methods=['POST'])
@require_api_key
def register_client():
    data = request.get_json()
    
    # Validate client data
    if not data.get('first_name') or not data.get('last_name') or not validate_date(data.get('date_of_birth')):
        return jsonify({'error': 'Validation Error', 'message': 'First name, last name, and date of birth are required'}), 400

    new_client = Client(
        first_name=data['first_name'].strip(),
        last_name=data['last_name'].strip(),
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
        contact_info=data.get('contact_info', '')[:100]
    )
    
    try:
        db.session.add(new_client)
        db.session.commit()
        return jsonify({"message": "Client registered", "id": new_client.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database Error"}), 500

# Search clients by name (first or last)
@app.route('/clients', methods=['GET'])
def search_clients():
    search_term = request.args.get('q', '')
    if len(search_term) < 2:
        return jsonify({'error': 'Validation Error', 'message': 'Search term must be at least 2 characters'}), 400
    
    clients = Client.query.filter(
        (Client.first_name.contains(search_term)) | 
        (Client.last_name.contains(search_term))
    ).limit(50).all()

    return jsonify([{"id": c.id, "name": f"{c.first_name} {c.last_name}", "dob": str(c.date_of_birth)} for c in clients])

# Get client's profile (including enrolled programs)
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
        "programs": [{"id": cp.program.id, "name": cp.program.name, "enrollment_date": str(cp.enrollment_date), "notes": cp.notes} for cp in programs]
    })

# Enroll client into a program
@app.route('/clients/<int:client_id>/programs', methods=['POST'])
@require_api_key
def enroll_client(client_id):
    data = request.get_json()
    
    # Validate program ID
    if not data.get('program_id') or not HealthProgram.query.get(data['program_id']):
        return jsonify({'error': 'Validation Error', 'message': 'Valid program_id is required'}), 400

    enrollment = ClientProgram(
        client_id=client_id,
        program_id=data['program_id'],
        enrollment_date=datetime.now().date(),
        notes=data.get('notes', '')[:500]
    )

    try:
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({"message": "Client enrolled in program"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database Error"}), 500

# =========================
# Main Application
# =========================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(host='0.0.0.0', port=5000, debug=True)
