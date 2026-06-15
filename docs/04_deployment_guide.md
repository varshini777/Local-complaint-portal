# Deployment Guide

## Recommended Deployment Stack

- Python 3.10+
- MySQL 8+
- Gunicorn or Waitress
- Nginx or Apache reverse proxy
- Windows Server or Linux server

## Environment Configuration

Create a production `.env` file:

```text
FLASK_ENV=production
SECRET_KEY=replace-with-strong-random-secret
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=portal_user
MYSQL_PASSWORD=strong_password
MYSQL_DATABASE=local_complaint_portal
```

## Production Checklist

- Use a strong `SECRET_KEY`.
- Use a dedicated MySQL user.
- Disable debug mode.
- Restrict upload folder permissions.
- Configure HTTPS.
- Back up the database regularly.
- Back up uploaded images.
- Keep dependencies updated.

## Database Deployment

Run:

```bash
mysql -u portal_user -p < database/complaint_portal.sql
```

Seed required default data:

```bash
flask --app run.py seed-data
```

## Running With Waitress

Install Waitress:

```bash
pip install waitress
```

Run:

```bash
waitress-serve --listen=0.0.0.0:5000 run:app
```

## Static Uploads

Uploaded files are stored under:

```text
backend/static/uploads/
```

Ensure this folder is writable by the application user.

