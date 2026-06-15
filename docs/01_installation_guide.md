# Installation Guide

## Project

**Local Complaint Portal: A Web-Based Civic Complaint Management System**

## Prerequisites

- Python 3.10 or later
- MySQL 8.0 or later
- Git
- VS Code or any Python IDE

## Setup Steps

1. Clone or open the project folder.

   ```bash
   cd Local_complaint
   ```

2. Create a virtual environment.

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment.

   Windows:

   ```bash
   .venv\Scripts\activate
   ```

4. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

5. Create the database.

   ```bash
   mysql -u root -p < database/complaint_portal.sql
   ```

6. Create environment file.

   ```bash
   copy .env.example .env
   ```

7. Update `.env` with MySQL credentials.

   ```text
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=local_complaint_portal
   ```

8. Seed default data.

   ```bash
   flask --app run.py seed-data
   ```

9. Run the project.

   ```bash
   python run.py
   ```

10. Open the application.

   ```text
   http://127.0.0.1:5000
   ```

## Default Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@localportal.com | Admin@123 |
| Officer | officer@localportal.com | Officer@123 |

Citizens can register through the registration page.

