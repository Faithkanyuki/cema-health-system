Overview
The CEMA Health Information System is a simple web-based application designed to manage health programs and client data. It provides essential functionalities such as program creation, client registration, program enrollment, and client search. The system also exposes a REST API to allow integration with other systems.

Features
Create Health Programs: Manage programs such as TB, Malaria, HIV, etc.
Register Clients: Register new clients with personal details.
Enroll Clients in Programs: Link clients to health programs for monitoring and management.
Search for Clients: Search for clients by name.
Client Profiles: View detailed client profiles with their program enrollments.
REST API Integration: Expose essential endpoints for program and client management.

Key Technologies
Backend: Python, Flask
Database: SQLite (SQLAlchemy ORM)
Testing Framework: Pytest
Docker: Containerization for deployment

Setup Instructions
Prerequisites
Ensure you have the following installed:

Python 3.x
pip
Docker (optional, for containerized deployment)

Clone the Repository
git clone <your-repository-url>
cd CEMA-Health-

Install Dependencies
pip install -r requirements.txt
Run the Application

bash
Copy
Edit
python app.py
This will start the Flask server on http://localhost:5000.
API Key (For Secure Access)

The API requires an API key in the request header (X-API-Key). The default key is admin

Running with Docker
If you prefer to run the application with Docker:

docker-compose build
Run the Application
docker-compose up
This will start the application and map port 5000.


API Endpoints

Health Program Endpoints
Create Program

POST /programs
Request Body:
json

{
  "name": "Malaria",
  "description": "Malaria Prevention Program"
}
Response:

json
{
  "message": "Program created",
  "id": 1
}
List Programs

GET /programs

Response:
json

[
  {
    "id": 1,
    "name": "Malaria",
    "description": "Malaria Prevention Program"
  }
]
Client Endpoints
Register Client

POST /clients

Request Body:

json

{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-01",
  "contact_info": "john@example.com"
}
Search Clients

GET /clients?q=<search_term>

Example: /clients?q=John

Response:

json

[
  {
    "id": 1,
    "name": "John Doe",
    "dob": "1990-01-01"
  }
]
Get Client Profile

GET /clients/<client_id>

Response:

json

{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "dob": "1990-01-01",
  "contact_info": "john@example.com",
  "programs": [
    {
      "id": 1,
      "name": "Malaria",
      "enrollment_date": "2025-04-01",
      "notes": "Initial enrollment"
    }
  ]
}
Enroll Client in Program

POST /clients/<client_id>/programs

Request Body:

json

{
  "program_id": 1,
  "notes": "First enrollment for Malaria"
}


