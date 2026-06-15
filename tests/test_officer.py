from backend.extensions import db
from backend.models import ActivityLog, Complaint, Notification
from tests.conftest import login


def test_officer_can_update_assigned_complaint_status(client, app, sample_complaint):
    login(client, "officer@localportal.com", "Officer@123")
    response = client.post(
        f"/officer/complaints/{sample_complaint.complaint_id}/status",
        data={"status": Complaint.STATUS_IN_PROGRESS, "remarks": "Work started."},
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        complaint = db.session.get(Complaint, sample_complaint.complaint_id)
        assert complaint.status == Complaint.STATUS_IN_PROGRESS
        assert ActivityLog.query.filter_by(action="Complaint Status Update").count() == 1
        assert Notification.query.filter_by(complaint_id=complaint.complaint_id).count() >= 1


def test_officer_can_resolve_assigned_complaint(client, app, sample_complaint):
    login(client, "officer@localportal.com", "Officer@123")
    client.post(
        f"/officer/complaints/{sample_complaint.complaint_id}/status",
        data={"status": Complaint.STATUS_IN_PROGRESS, "remarks": "Work started."},
    )
    response = client.post(
        f"/officer/complaints/{sample_complaint.complaint_id}/resolve",
        data={
            "resolution_notes": "Issue repaired successfully.",
            "work_performed": "Filled damaged section.",
            "materials_used": "Asphalt",
            "additional_remarks": "Site cleaned.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        complaint = db.session.get(Complaint, sample_complaint.complaint_id)
        assert complaint.status == Complaint.STATUS_RESOLVED
        assert complaint.resolved_at is not None
        assert ActivityLog.query.filter_by(action="Complaint Resolution").count() == 1
