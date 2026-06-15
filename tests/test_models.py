import pytest
from datetime import datetime, timezone
from backend.models import (
    Complaint,
    ComplaintCategory,
    ComplaintUpdate,
    Feedback,
    Notification,
    SystemSetting,
    User,
    Ward,
)
from backend.extensions import db


def test_user_password_hashing(app):
    with app.app_context():
        user = User(
            full_name="Test User",
            email="test@example.com",
            phone="9999999999",
            role=User.ROLE_CITIZEN,
        )
        user.set_password("Test@123")
        db.session.add(user)
        db.session.commit()

        assert user.check_password("Test@123") is True
        assert user.check_password("wrong") is False


def test_user_security_answer_hashing(app):
    with app.app_context():
        user = User(
            full_name="Test User",
            email="test@example.com",
            phone="9999999999",
            role=User.ROLE_CITIZEN,
        )
        user.set_security_answer("answer")
        db.session.add(user)
        db.session.commit()

        assert user.check_security_answer("answer") is True
        assert user.check_security_answer("wrong") is False


def test_user_role_properties(app):
    with app.app_context():
        admin = User(
            full_name="Admin",
            email="admin@example.com",
            phone="9999999999",
            role=User.ROLE_ADMIN,
        )
        citizen = User(
            full_name="Citizen",
            email="citizen@example.com",
            phone="9999999999",
            role=User.ROLE_CITIZEN,
        )
        officer = User(
            full_name="Officer",
            email="officer@example.com",
            phone="9999999999",
            role=User.ROLE_OFFICER,
        )
        db.session.add_all([admin, citizen, officer])
        db.session.commit()

        assert admin.is_admin is True
        assert admin.is_citizen is False
        assert admin.is_officer is False

        assert citizen.is_admin is False
        assert citizen.is_citizen is True
        assert citizen.is_officer is False

        assert officer.is_admin is False
        assert officer.is_citizen is False
        assert officer.is_officer is True


def test_ward_display_name(app):
    with app.app_context():
        ward = Ward(
            ward_name="Test Ward",
            ward_code="T001",
            is_active=True,
        )
        db.session.add(ward)
        db.session.commit()

        assert ward.display_name == "T001 - Test Ward"


def test_complaint_category_active_filter(app):
    with app.app_context():
        active = ComplaintCategory(
            category_name="Active Category",
            description="Test",
            is_active=True,
        )
        inactive = ComplaintCategory(
            category_name="Inactive Category",
            description="Test",
            is_active=False,
        )
        db.session.add_all([active, inactive])
        db.session.commit()

        active_categories = ComplaintCategory.query.filter_by(is_active=True).all()
        assert len(active_categories) == 1
        assert active_categories[0].category_name == "Active Category"


def test_complaint_number_generation(app, citizen, category, ward):
    with app.app_context():
        complaint = Complaint(
            title="Test Complaint",
            description="Test description",
            category_id=category.category_id,
            priority=Complaint.PRIORITY_MEDIUM,
            status=Complaint.STATUS_SUBMITTED,
            location="Test Location",
            ward_id=ward.ward_id,
            citizen_id=citizen.user_id,
            is_active=True,
        )
        db.session.add(complaint)
        db.session.flush()

        complaint.assign_complaint_number()
        db.session.commit()

        assert complaint.complaint_number is not None
        assert complaint.complaint_number.startswith("LCP-")


def test_complaint_timeline_property(app, complaint, citizen):
    with app.app_context():
        update = ComplaintUpdate(
            complaint_id=complaint.complaint_id,
            updated_by=citizen.user_id,
            status=Complaint.STATUS_SUBMITTED,
            action="Test Action",
            remarks="Test remarks",
        )
        db.session.add(update)
        db.session.commit()

        timeline = complaint.timeline
        assert len(timeline) == 1
        assert timeline[0].action == "Test Action"


def test_complaint_has_image_properties(app, complaint):
    with app.app_context():
        complaint.before_image_path = "uploads/test/before.jpg"
        complaint.after_image_path = "uploads/test/after.jpg"
        db.session.commit()

        assert complaint.has_before_image is True
        assert complaint.has_after_image is True


def test_complaint_has_resolution_property(app, complaint):
    with app.app_context():
        complaint.resolution_notes = "Test resolution"
        db.session.commit()

        assert complaint.has_resolution is True


def test_notification_mark_read(app, citizen, complaint):
    with app.app_context():
        notification = Notification(
            user_id=citizen.user_id,
            complaint_id=complaint.complaint_id,
            notification_type="Test",
            message="Test message",
            is_read=False,
            is_active=True,
        )
        db.session.add(notification)
        db.session.commit()

        assert notification.is_read is False

        notification.mark_as_read()
        db.session.commit()

        assert notification.is_read is True


def test_feedback_rating_validation(app, complaint, citizen):
    with app.app_context():
        feedback = Feedback(
            complaint_id=complaint.complaint_id,
            citizen_id=citizen.user_id,
            rating=5,
            comment="Great service",
            is_active=True,
        )
        db.session.add(feedback)
        db.session.commit()

        assert feedback.rating == 5
        assert feedback.comment == "Great service"


def test_system_setting_typed_value(app):
    with app.app_context():
        int_setting = SystemSetting(
            setting_key="test_int",
            setting_value="42",
            setting_type=SystemSetting.TYPE_INTEGER,
            is_active=True,
        )
        str_setting = SystemSetting(
            setting_key="test_str",
            setting_value="test",
            setting_type=SystemSetting.TYPE_STRING,
            is_active=True,
        )
        db.session.add_all([int_setting, str_setting])
        db.session.commit()

        assert int_setting.typed_value == 42
        assert str_setting.typed_value == "test"
