import pytest
from backend.forms.auth_forms import (
    ForgotPasswordForm,
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
)
from backend.forms.citizen_forms import ChangePasswordForm, ComplaintForm, ProfileUpdateForm
from backend.forms.officer_forms import (
    ComplaintResolutionForm,
    ComplaintStatusForm,
    OfficerChangePasswordForm,
    OfficerProfileForm,
)


def test_login_form_valid_data():
    form = LoginForm(
        email="test@example.com",
        password="Test@123",
        remember_me=True,
    )
    assert form.validate() is True


def test_login_form_missing_email():
    form = LoginForm(email="", password="Test@123")
    assert form.validate() is False
    assert "email" in form.errors


def test_login_form_missing_password():
    form = LoginForm(email="test@example.com", password="")
    assert form.validate() is False
    assert "password" in form.errors


def test_registration_form_valid_data():
    form = RegistrationForm(
        full_name="Test User",
        email="test@example.com",
        phone="9999999999",
        password="Test@123",
        confirm_password="Test@123",
        security_question="What is your project code?",
        security_answer="portal",
    )
    assert form.validate() is True


def test_registration_form_password_mismatch():
    form = RegistrationForm(
        full_name="Test User",
        email="test@example.com",
        phone="9999999999",
        password="Test@123",
        confirm_password="Different@123",
        security_question="What is your project code?",
        security_answer="portal",
    )
    assert form.validate() is False
    assert "confirm_password" in form.errors


def test_registration_form_weak_password():
    form = RegistrationForm(
        full_name="Test User",
        email="test@example.com",
        phone="9999999999",
        password="weak",
        confirm_password="weak",
        security_question="What is your project code?",
        security_answer="portal",
    )
    assert form.validate() is False


def test_forgot_password_form_valid_email():
    form = ForgotPasswordForm(email="test@example.com")
    assert form.validate() is True


def test_forgot_password_form_invalid_email():
    form = ForgotPasswordForm(email="invalid-email")
    assert form.validate() is False
    assert "email" in form.errors


def test_reset_password_form_valid_data():
    form = ResetPasswordForm(
        security_answer="answer",
        password="New@123",
        confirm_password="New@123",
    )
    assert form.validate() is True


def test_reset_password_form_password_mismatch():
    form = ResetPasswordForm(
        security_answer="answer",
        password="New@123",
        confirm_password="Different@123",
    )
    assert form.validate() is False


def test_complaint_form_valid_data():
    form = ComplaintForm(
        title="Test Complaint",
        description="Test description with enough characters",
        category=1,
        priority="Medium",
        location="Test Location",
        ward=1,
    )
    assert form.validate() is True


def test_complaint_form_title_too_short():
    form = ComplaintForm(
        title="Short",
        description="Test description with enough characters",
        category=1,
        priority="Medium",
        location="Test Location",
        ward=1,
    )
    assert form.validate() is False
    assert "title" in form.errors


def test_complaint_form_description_too_short():
    form = ComplaintForm(
        title="Test Complaint Title",
        description="Short",
        category=1,
        priority="Medium",
        location="Test Location",
        ward=1,
    )
    assert form.validate() is False
    assert "description" in form.errors


def test_profile_update_form_valid_data():
    form = ProfileUpdateForm(
        full_name="Test User",
        phone="9999999999",
    )
    assert form.validate() is True


def test_profile_update_form_invalid_phone():
    form = ProfileUpdateForm(
        full_name="Test User",
        phone="invalid",
    )
    assert form.validate() is False
    assert "phone" in form.errors


def test_change_password_form_valid_data():
    form = ChangePasswordForm(
        current_password="Old@123",
        new_password="New@123",
        confirm_password="New@123",
    )
    assert form.validate() is True


def test_change_password_form_new_password_too_short():
    form = ChangePasswordForm(
        current_password="Old@123",
        new_password="short",
        confirm_password="short",
    )
    assert form.validate() is False


def test_officer_profile_form_valid_data():
    form = OfficerProfileForm(
        full_name="Officer Name",
        phone="9999999999",
    )
    assert form.validate() is True


def test_complaint_status_form_valid_data():
    form = ComplaintStatusForm(status="In Progress", remarks="Test remarks")
    assert form.validate() is True


def test_complaint_resolution_form_valid_data():
    form = ComplaintResolutionForm(
        resolution_notes="Test resolution",
        work_performed="Test work",
    )
    assert form.validate() is True


def test_officer_change_password_form_valid_data():
    form = OfficerChangePasswordForm(
        current_password="Old@123",
        new_password="New@123",
        confirm_password="New@123",
    )
    assert form.validate() is True
