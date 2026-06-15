# Local Complaint Portal

Local Complaint Portal is an MCA major project for a web-based civic complaint
management system.

This repository currently contains Phase 1 and Phase 2 of the implementation:
the project structure, Flask application factory, configuration, extensions, and
safe placeholders for later modules.

## Current Phase

- Folder structure is ready.
- Flask app factory is configured.
- SQLAlchemy, Flask-Migrate, and Flask-Login extensions are initialized.
- Upload directories are created automatically at startup.
- Database schema, models, routes, and authentication behavior are planned for
  later phases.

## Setup

1. Create a virtual environment.

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies.

   ```powershell
   pip install -r requirements.txt
   ```

3. Copy the example environment file.

   ```powershell
   Copy-Item .env.example .env
   ```

4. Update `.env` with your MySQL credentials.

5. Start the development server.

   ```powershell
   python run.py
   ```

6. Open `http://127.0.0.1:5000`.

## Phase Notes

The database schema will be implemented in Phase 3. SQLAlchemy models will be
implemented in Phase 4. Authentication routes and session behavior will be
implemented in Phase 6.
