# CEMA Health Information System

A secure health information system API for managing clients and health programs.

## Features

- **Program Management**: Create and view health programs (TB, Malaria, HIV, etc.)
- **Client Management**: Register and search for clients
- **Enrollment System**: Enroll clients in multiple programs
- **Comprehensive Profiles**: View client details with enrollment history
- **REST API**: JSON-based endpoints for easy integration

## Setup

### Local Development
```bash
# 1. Clone repository
git clone https://github.com/yourusername/cema-health-system.git
cd cema-health-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python -c "from app import app, db; with app.app_context(): db.create_all()"

# 4. Run application
python app.py