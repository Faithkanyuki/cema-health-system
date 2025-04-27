# CEMA Health Information System

A basic health information system for managing clients and health programs.

## Features
- Create health programs (TB, Malaria, HIV, etc.)
- Register new clients
- Enroll clients in programs
- Search for clients
- View client profiles with program enrollment
- REST API for integration

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`

## API Endpoints

- `POST /programs` - Create a new health program
- `GET /programs` - List all programs
- `POST /clients` - Register a new client
- `GET /clients?q=<search>` - Search clients
- `GET /clients/<id>` - Get client profile
- `POST /clients/<id>/programs` - Enroll client in program

## Deployment

Using Docker: