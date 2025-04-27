from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class HealthProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    contact_info = db.Column(db.String(100))
    
class ClientProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('health_program.id'), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    
    client = db.relationship('Client', backref='programs')
    program = db.relationship('HealthProgram', backref='clients')