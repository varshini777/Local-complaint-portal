# MCA Viva Questions and Answers

## 1. What is the objective of this project?

The objective is to provide a web-based civic complaint management system where citizens can submit complaints, officers can resolve assigned complaints, and admins can manage users, wards, assignments, reports, and system settings.

## 2. Which technology stack is used?

The project uses Python Flask, MySQL, SQLAlchemy, Flask-Login, Flask-WTF, bcrypt, Bootstrap 5, JavaScript, and Chart.js.

## 3. Why did you use Flask?

Flask is lightweight, flexible, and suitable for academic web applications. It allows modular development through blueprints and integrates well with SQLAlchemy and MySQL.

## 4. Why was Flask-Login used instead of JWT?

The application is server-rendered, not a separate SPA frontend. Flask-Login session authentication is simpler and more suitable for this architecture.

## 5. How are passwords stored?

Passwords are hashed using bcrypt. Plain text passwords are never stored.

## 6. What are the user roles?

The system has three roles:

- Citizen
- Officer
- Admin

## 7. How is role-based access implemented?

Custom decorators such as `admin_required`, `officer_required`, and `citizen_required` protect role-specific routes.

## 8. What is soft delete?

Soft delete means records are not permanently removed. Instead, `is_active` is used to mark records inactive while preserving history.

## 9. What is the purpose of wards?

Wards represent local civic areas. Complaints belong to wards, and officers can be assigned to wards.

## 10. How is complaint tracking done?

Each complaint status change creates a `complaint_updates` record, forming a timeline.

## 11. How are notifications generated?

Notification service functions create records when complaints are submitted, assigned, updated, resolved, or closed.

## 12. How are reports generated?

Reports use SQLAlchemy queries for analytics and CSV export functions for downloadable data.

## 13. What is Chart.js used for?

Chart.js displays category distribution, ward analytics, officer performance, escalation analytics, monthly trends, complaint aging, and feedback ratings.

## 14. How does file upload work?

Images are validated by extension and size, renamed securely, and stored in local upload folders.

## 15. What testing was done?

A pytest suite verifies registration, login, complaint submission, assignment, resolution, closure, reports dashboard, and CSV exports using Flask test client and SQLite test database.

