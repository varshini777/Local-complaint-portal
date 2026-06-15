from backend.models import ActivityLog, User
from backend.extensions import db
from tests.conftest import login


def test_registration_creates_citizen(client, app):
    response = client.post(
        "/register",
        data={
            "full_name": "New Citizen",
            "email": "newcitizen@example.com",
            "phone": "9999999999",
            "password": "Citizen@123",
            "confirm_password": "Citizen@123",
            "security_question": "What is your project code?",
            "security_answer": "portal",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        user = User.query.filter_by(email="newcitizen@example.com").first()
        assert user is not None
        assert user.role == User.ROLE_CITIZEN
        assert user.check_password("Citizen@123")
        assert ActivityLog.query.filter_by(action="Citizen Registration").count() == 1


def test_login_success_creates_activity_log(client, app, citizen):
    response = login(client, citizen.email, citizen.password)

    assert response.status_code == 302
    with app.app_context():
        assert ActivityLog.query.filter_by(action="Login").count() == 1


def test_password_reset_with_security_answer(client, app, citizen):
    client.post("/forgot-password", data={"email": citizen.email})
    response = client.post(
        "/reset-password",
        data={
            "security_answer": "alpha",
            "password": "Citizen@456",
            "confirm_password": "Citizen@456",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        refreshed = db.session.get(User, citizen.user_id)
        assert refreshed.check_password("Citizen@456")
        assert ActivityLog.query.filter_by(action="Password Reset").count() == 1
