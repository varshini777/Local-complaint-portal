import pytest
from datetime import datetime, timezone
from backend.models import ActivityLog, Complaint, ComplaintCategory, User, Ward
from backend.services.activity_log_service import log_activity
from backend.services.auth_service import (
    authenticate_user,
    check_user_exists,
    initiate_password_reset,
    validate_password_reset_session,
)
from backend.services.escalation_service import check_escalation_required, escalate_complaint
from backend.services.file_service import allowed_upload, save_before_image
from backend.extensions import db


def test_log_activity_creates_log_entry(app, citizen):
    with app.app_context():
        log_activity("Test Action", citizen, "Test details")
        log = ActivityLog.query.filter_by(action="Test Action").first()
        assert log is not None
        assert log.user_id == citizen.user_id
        assert log.details == "Test details"


def test_log_activity_without_user(app):
    with app.app_context():
        log_activity("System Action", None, "System details")
        log = ActivityLog.query.filter_by(action="System Action").first()
        assert log is not None
        assert log.user_id is None


def test_authenticate_user_success(app, citizen):
    with app.app_context():
        user = authenticate_user(citizen.email, "citizen123")
        assert user is not None
        assert user.user_id == citizen.user_id


def test_authenticate_user_wrong_password(app, citizen):
    with app.app_context():
        user = authenticate_user(citizen.email, "wrongpassword")
        assert user is None


def test_authenticate_user_nonexistent(app):
    with app.app_context():
        user = authenticate_user("nonexistent@example.com", "password")
        assert user is None


def test_check_user_exists_active(app, citizen):
    with app.app_context():
        user = check_user_exists(citizen.email)
        assert user is not None
        assert user.user_id == citizen.user_id


def test_check_user_exists_inactive(app, citizen):
    with app.app_context():
        citizen.is_active = False
        db.session.commit()
        user = check_user_exists(citizen.email)
        assert user is None


def test_check_user_exists_nonexistent(app):
    with app.app_context():
        user = check_user_exists("nonexistent@example.com")
        assert user is None


def test_initiate_password_reset_success(app, citizen):
    with app.app_context():
        citizen.security_question = "Test Question"
        citizen.security_answer_hash = "hashed_answer"
        db.session.commit()
        result = initiate_password_reset(citizen)
        assert result is True


def test_initiate_password_reset_no_security_details(app, citizen):
    with app.app_context():
        citizen.security_question = None
        db.session.commit()
        result = initiate_password_reset(citizen)
        assert result is False


def test_validate_password_reset_session_valid(app, citizen, client):
    with app.app_context():
        client.post("/forgot-password", data={"email": citizen.email})
        is_valid, user_id, error = validate_password_reset_session()
        assert is_valid is True
        assert user_id == citizen.user_id
        assert error is None


def test_validate_password_reset_session_no_session(app):
    from flask import session

    with app.test_request_context():
        is_valid, user_id, error = validate_password_reset_session()
        assert is_valid is False
        assert user_id is None
        assert error is not None


def test_check_escalation_required_urgent(app, complaint):
    with app.app_context():
        complaint.submitted_at = datetime.now(timezone.utc)
        complaint.status = Complaint.STATUS_IN_PROGRESS
        db.session.commit()
        result = check_escalation_required(complaint, 7, 15)
        assert result == Complaint.ESCALATION_URGENT


def test_check_escalation_required_critical(app, complaint):
    with app.app_context():
        complaint.submitted_at = datetime.now(timezone.utc)
        complaint.status = Complaint.STATUS_IN_PROGRESS
        db.session.commit()
        result = check_escalation_required(complaint, 7, 15)
        assert result == Complaint.ESCALATION_CRITICAL


def test_check_escalation_required_normal(app, complaint):
    with app.app_context():
        complaint.submitted_at = datetime.now(timezone.utc)
        complaint.status = Complaint.STATUS_IN_PROGRESS
        db.session.commit()
        result = check_escalation_required(complaint, 7, 15)
        assert result == Complaint.ESCALATION_NORMAL


def test_escalate_complaint(app, complaint):
    with app.app_context():
        escalate_complaint(complaint, Complaint.ESCALATION_URGENT)
        assert complaint.escalation_level == Complaint.ESCALATION_URGENT


def test_allowed_upload_valid_extension(app):
    with app.app_context():
        assert allowed_upload("test.jpg") is True
        assert allowed_upload("test.png") is True
        assert allowed_upload("test.webp") is True


def test_allowed_upload_invalid_extension(app):
    with app.app_context():
        assert allowed_upload("test.exe") is False
        assert allowed_upload("test.pdf") is False


def test_allowed_upload_no_extension(app):
    with app.app_context():
        assert allowed_upload("test") is False
