from pathlib import Path
from types import SimpleNamespace

import pytest

from backend import create_app
from backend.extensions import db
from backend.models import (
    Complaint,
    ComplaintCategory,
    ComplaintUpdate,
    User,
    Ward,
)
from backend.services.seed_service import seed_development_data


class TestConfig:
    SECRET_KEY = "test-secret"
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = Path("backend/static/uploads")
    COMPLAINT_BEFORE_UPLOAD_FOLDER = Path("backend/static/uploads/complaints/before")
    COMPLAINT_AFTER_UPLOAD_FOLDER = Path("backend/static/uploads/complaints/after")
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    DEBUG = True


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        seed_development_data()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def citizen(app):
    with app.app_context():
        user = User(
            full_name="Test Citizen",
            email="citizen@example.com",
            phone="7777777777",
            role=User.ROLE_CITIZEN,
            security_question="What is your test code?",
            is_active=True,
        )
        user.set_password("Citizen@123")
        user.set_security_answer("alpha")
        db.session.add(user)
        db.session.commit()
        return SimpleNamespace(
            user_id=user.user_id,
            email="citizen@example.com",
            password="Citizen@123",
        )


@pytest.fixture()
def sample_complaint(app, citizen):
    with app.app_context():
        category = ComplaintCategory.query.first()
        ward = Ward.query.first()
        officer = User.query.filter_by(role=User.ROLE_OFFICER).first()
        complaint = Complaint(
            title="Damaged road",
            description="Road surface is damaged near the bus stop.",
            category_id=category.category_id,
            priority=Complaint.PRIORITY_HIGH,
            status=Complaint.STATUS_ASSIGNED,
            escalation_level=Complaint.ESCALATION_NORMAL,
            location="Main Road",
            ward_id=ward.ward_id,
                citizen_id=citizen.user_id,
            assigned_officer_id=officer.user_id,
            is_active=True,
        )
        db.session.add(complaint)
        db.session.flush()
        db.session.add(
            ComplaintUpdate(
                complaint_id=complaint.complaint_id,
                updated_by=citizen.user_id,
                status=Complaint.STATUS_SUBMITTED,
                action="Complaint Submitted",
                remarks="Initial complaint.",
            )
        )
        db.session.commit()
        return SimpleNamespace(
            complaint_id=complaint.complaint_id,
            complaint_number=complaint.complaint_number,
        )


def login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def logout(client):
    return client.get("/logout", follow_redirects=False)
