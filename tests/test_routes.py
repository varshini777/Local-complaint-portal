import pytest
from backend.models import Complaint, ComplaintCategory, User, Ward
from backend.extensions import db


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200


def test_register_route_get(client):
    response = client.get("/register")
    assert response.status_code == 200


def test_login_route_get(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_forgot_password_route_get(client):
    response = client.get("/forgot-password")
    assert response.status_code == 200


def test_citizen_dashboard_requires_login(client):
    response = client.get("/citizen/dashboard")
    assert response.status_code == 302
    assert "/login" in response.location


def test_officer_dashboard_requires_login(client):
    response = client.get("/officer/dashboard")
    assert response.status_code == 302
    assert "/login" in response.location


def test_admin_dashboard_requires_login(client):
    response = client.get("/admin/dashboard")
    assert response.status_code == 302
    assert "/login" in response.location


def test_citizen_dashboard_authenticated(client, citizen):
    from tests.conftest import login

    login(client, citizen.email, citizen.password)
    response = client.get("/citizen/dashboard")
    assert response.status_code == 200


def test_officer_dashboard_authenticated(client, officer):
    from tests.conftest import login

    login(client, officer.email, officer.password)
    response = client.get("/officer/dashboard")
    assert response.status_code == 200


def test_admin_dashboard_authenticated(client, admin):
    from tests.conftest import login

    login(client, admin.email, admin.password)
    response = client.get("/admin/dashboard")
    assert response.status_code == 200


def test_citizen_cannot_access_admin_dashboard(client, citizen):
    from tests.conftest import login

    login(client, citizen.email, citizen.password)
    response = client.get("/admin/dashboard")
    assert response.status_code == 403


def test_officer_cannot_access_admin_dashboard(client, officer):
    from tests.conftest import login

    login(client, officer.email, officer.password)
    response = client.get("/admin/dashboard")
    assert response.status_code == 403


def test_citizen_cannot_access_officer_dashboard(client, citizen):
    from tests.conftest import login

    login(client, citizen.email, citizen.password)
    response = client.get("/officer/dashboard")
    assert response.status_code == 403


def test_officer_cannot_access_citizen_dashboard(client, officer):
    from tests.conftest import login

    login(client, officer.email, officer.password)
    response = client.get("/citizen/dashboard")
    assert response.status_code == 403


def test_logout_route(client, citizen):
    from tests.conftest import login

    login(client, citizen.email, citizen.password)
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.location


def test_complaint_history_route_authenticated(client, citizen):
    from tests.conftest import login

    login(client, citizen.email, citizen.password)
    response = client.get("/citizen/complaints")
    assert response.status_code == 200


def test_notifications_route_authenticated(client, citizen):
    from tests.conftest import login

    login(client, citizen.email, citizen.password)
    response = client.get("/citizen/notifications")
    assert response.status_code == 200


def test_profile_route_authenticated(client, citizen):
    from tests.conftest import login

    login(client, citizen.email, citizen.password)
    response = client.get("/citizen/profile")
    assert response.status_code == 200


def test_change_password_route_authenticated(client, citizen):
    from tests.conftest import login

    login(client, citizen.email, citizen.password)
    response = client.get("/citizen/change-password")
    assert response.status_code == 200


def test_officer_assigned_complaints_authenticated(client, officer):
    from tests.conftest import login

    login(client, officer.email, officer.password)
    response = client.get("/officer/complaints")
    assert response.status_code == 200


def test_admin_users_route_authenticated(client, admin):
    from tests.conftest import login

    login(client, admin.email, admin.password)
    response = client.get("/admin/users")
    assert response.status_code == 200


def test_admin_wards_route_authenticated(client, admin):
    from tests.conftest import login

    login(client, admin.email, admin.password)
    response = client.get("/admin/wards")
    assert response.status_code == 200


def test_admin_complaints_route_authenticated(client, admin):
    from tests.conftest import login

    login(client, admin.email, admin.password)
    response = client.get("/admin/complaints")
    assert response.status_code == 200


def test_admin_settings_route_authenticated(client, admin):
    from tests.conftest import login

    login(client, admin.email, admin.password)
    response = client.get("/admin/settings")
    assert response.status_code == 200


def test_admin_activity_logs_route_authenticated(client, admin):
    from tests.conftest import login

    login(client, admin.email, admin.password)
    response = client.get("/admin/activity-logs")
    assert response.status_code == 200
