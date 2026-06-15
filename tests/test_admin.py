from backend.extensions import db
from backend.models import ActivityLog, Complaint, User, Ward
from tests.conftest import login


def test_admin_can_create_officer(client, app):
    login(client, "admin@localportal.com", "Admin@123")
    response = client.post(
        "/admin/officers/new",
        data={
            "full_name": "Second Officer",
            "email": "second.officer@example.com",
            "phone": "8888887777",
            "password": "Officer@123",
            "is_active": "y",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        officer = User.query.filter_by(email="second.officer@example.com").first()
        assert officer is not None
        assert officer.role == User.ROLE_OFFICER
        assert ActivityLog.query.filter_by(action="Officer Created").count() == 1


def test_admin_can_create_ward_and_assign_complaint(client, app, sample_complaint):
    login(client, "admin@localportal.com", "Admin@123")
    officer = User.query.filter_by(email="officer@localportal.com").first()

    ward_response = client.post(
        "/admin/wards/new",
        data={
            "ward_name": "Ward 2",
            "ward_code": "W002",
            "assigned_officer_id": str(officer.user_id),
            "is_active": "y",
        },
        follow_redirects=False,
    )
    assign_response = client.post(
        f"/admin/complaints/{sample_complaint.complaint_id}/assign",
        data={"assigned_officer_id": str(officer.user_id)},
        follow_redirects=False,
    )

    assert ward_response.status_code == 302
    assert assign_response.status_code == 302
    with app.app_context():
        assert Ward.query.filter_by(ward_code="W002").first() is not None
        complaint = db.session.get(Complaint, sample_complaint.complaint_id)
        assert complaint.assigned_officer_id == officer.user_id


def test_admin_can_close_resolved_complaint(client, app, sample_complaint):
    login(client, "admin@localportal.com", "Admin@123")
    with app.app_context():
        complaint = db.session.get(Complaint, sample_complaint.complaint_id)
        complaint.status = Complaint.STATUS_RESOLVED
        db.session.commit()

    response = client.post(
        f"/admin/complaints/{sample_complaint.complaint_id}/close",
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        complaint = db.session.get(Complaint, sample_complaint.complaint_id)
        assert complaint.status == Complaint.STATUS_CLOSED
        assert complaint.closed_at is not None
