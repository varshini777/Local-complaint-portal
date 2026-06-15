# Project Architecture Overview

## Architecture Pattern

The project uses a modular Flask application factory architecture.

```text
Browser
  |
Bootstrap Templates
  |
Flask Routes
  |
Services
  |
SQLAlchemy Models
  |
MySQL Database
```

## Main Layers

### Presentation Layer

- HTML5
- Bootstrap 5
- JavaScript
- Chart.js
- Jinja templates

### Application Layer

- Flask routes
- Flask-Login session authentication
- Role-based access decorators
- Flask-WTF forms

### Business Logic Layer

- Notification service
- Report service
- Seed service
- File upload handling
- Activity logging

### Data Layer

- SQLAlchemy ORM
- MySQL database

## Blueprints

- `auth`
- `citizen`
- `officer`
- `admin`
- `reports`

## Security Design

- Password hashing with bcrypt
- Session authentication through Flask-Login
- CSRF protection through Flask-WTF
- Role-based route protection
- File upload validation
- Soft delete support
- Activity logs

## Complaint Workflow

```text
Submitted
  -> Assigned
  -> In Progress
  -> Resolved
  -> Closed
```

## Complaint Number

Complaint numbers are generated automatically:

```text
LCP-YYYY-XXXXXX
```

Example:

```text
LCP-2026-000015
```

