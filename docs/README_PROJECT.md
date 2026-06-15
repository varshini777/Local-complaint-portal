# Local Complaint Portal

**Local Complaint Portal: A Web-Based Civic Complaint Management System** is an MCA major project built using Flask, MySQL, SQLAlchemy, Bootstrap 5, and Chart.js.

## Features

- Citizen registration and login
- Officer and admin login
- Complaint submission with image upload
- Complaint tracking and timeline
- Notifications
- Ward management
- Officer assignment
- Complaint resolution
- Admin dashboard
- Reports and CSV exports
- Activity logging
- Automated tests

## Stack

- Python Flask
- MySQL
- SQLAlchemy
- Flask-Login
- Flask-WTF
- bcrypt
- Bootstrap 5
- JavaScript
- Chart.js
- pytest

## Default Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@localportal.com | Admin@123 |
| Officer | officer@localportal.com | Officer@123 |

## Run

```bash
pip install -r requirements.txt
mysql -u root -p < database/complaint_portal.sql
flask --app run.py seed-data
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

## Tests

```bash
pytest tests -q
```

## Documentation

See the `docs/` folder for installation, user manual, admin manual, deployment guide, database documentation, route documentation, architecture overview, viva questions, future enhancements, and conclusion.

