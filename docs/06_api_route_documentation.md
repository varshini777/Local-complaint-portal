# API and Route Documentation

This is a server-rendered Flask application. Most routes return HTML templates.

## Authentication Routes

| Method | Route | Description |
|---|---|---|
| GET/POST | `/register` | Citizen registration |
| GET/POST | `/login` | User login |
| GET | `/logout` | User logout |
| GET/POST | `/forgot-password` | Start password reset |
| GET/POST | `/reset-password` | Reset password using security answer |

## Citizen Routes

| Method | Route | Description |
|---|---|---|
| GET | `/citizen/dashboard` | Citizen dashboard |
| GET/POST | `/citizen/complaints/new` | Submit complaint |
| GET | `/citizen/complaints` | Complaint history |
| GET | `/citizen/complaints/<id>` | Complaint details |
| GET | `/citizen/notifications` | Notification center |
| POST | `/citizen/notifications/<id>/read` | Mark notification as read |
| POST | `/citizen/notifications/read-all` | Mark all notifications as read |
| GET/POST | `/citizen/profile` | Update profile |
| GET/POST | `/citizen/change-password` | Change password |

## Officer Routes

| Method | Route | Description |
|---|---|---|
| GET | `/officer/dashboard` | Officer dashboard |
| GET | `/officer/complaints` | Assigned complaints |
| GET | `/officer/complaints/<id>` | Complaint details |
| GET/POST | `/officer/complaints/<id>/status` | Update complaint status |
| GET/POST | `/officer/complaints/<id>/resolve` | Resolve complaint |
| GET/POST | `/officer/profile` | Update profile |
| GET/POST | `/officer/change-password` | Change password |

## Admin Routes

| Method | Route | Description |
|---|---|---|
| GET | `/admin/dashboard` | Admin dashboard |
| GET | `/admin/users` | Manage users |
| POST | `/admin/users/<id>/toggle-status` | Activate/deactivate user |
| GET/POST | `/admin/officers/new` | Create officer |
| GET/POST | `/admin/officers/<id>/edit` | Edit officer |
| GET | `/admin/wards` | Manage wards |
| GET/POST | `/admin/wards/new` | Create ward |
| GET/POST | `/admin/wards/<id>/edit` | Edit ward |
| POST | `/admin/wards/<id>/toggle-status` | Activate/deactivate ward |
| GET | `/admin/complaints` | Manage complaints |
| GET | `/admin/complaints/<id>` | Complaint details |
| POST | `/admin/complaints/<id>/assign` | Assign complaint |
| POST | `/admin/complaints/<id>/close` | Close complaint |
| GET/POST | `/admin/settings` | Manage system settings |
| GET | `/admin/activity-logs` | View activity logs |

## Report Routes

| Method | Route | Description |
|---|---|---|
| GET | `/admin/reports/` | Report dashboard |
| GET | `/admin/reports/export/complaints` | Complaint CSV export |
| GET | `/admin/reports/export/officers` | Officer CSV export |
| GET | `/admin/reports/export/feedback` | Feedback CSV export |

