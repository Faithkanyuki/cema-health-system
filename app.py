from flask import Flask, request, jsonify
from models import db, HealthProgram, Client, ClientProgram
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def home():
    return "Health Information System"

# Health Program Endpoints
@app.route('/programs', methods=['POST'])
def create_program():
    data = request.get_json()
    new_program = HealthProgram(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(new_program)
    db.session.commit()
    return jsonify({"message": "Program created", "id": new_program.id}), 201

@app.route('/programs', methods=['GET'])
def get_programs():
    programs = HealthProgram.query.all()
    return jsonify([{"id": p.id, "name": p.name} for p in programs])

# Client Endpoints
@app.route('/clients', methods=['POST'])
def register_client():
    data = request.get_json()
    new_client = Client(
        first_name=data['first_name'],
        last_name=data['last_name'],
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
        contact_info=data.get('contact_info', '')
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({"message": "Client registered", "id": new_client.id}), 201

@app.route('/clients', methods=['GET'])
def search_clients():
    search_term = request.args.get('q', '')
    clients = Client.query.filter(
        (Client.first_name.contains(search_term)) | 
        (Client.last_name.contains(search_term))
    ).all()
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
def enroll_client(client_id):
    data = request.get_json()
    enrollment = ClientProgram(
        client_id=client_id,
        program_id=data['program_id'],
        enrollment_date=datetime.now().date(),
        notes=data.get('notes', '')
    )
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({"message": "Client enrolled in program"}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)