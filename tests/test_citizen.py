from backend.models import ActivityLog, Complaint, Notification
from tests.conftest import login


def test_citizen_can_submit_complaint(client, app, citizen):
    with app.app_context():
        from backend.models import ComplaintCategory, Ward

        category = ComplaintCategory.query.first()
        ward = Ward.query.first()

    login(client, citizen.email, citizen.password)
    response = client.post(
        "/citizen/complaints/new",
        data={
            "title": "Broken streetlight",
            "description": "Streetlight has not worked for three nights.",
            "category": str(category.category_id),
            "priority": "Medium",
            "location": "Lake Street",
            "ward": str(ward.ward_id),
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    with app.app_context():
        complaint = Complaint.query.filter_by(title="Broken streetlight").first()
        assert complaint is not None
        assert complaint.status == Complaint.STATUS_SUBMITTED
        assert complaint.complaint_number.startswith("LCP-")
        assert Notification.query.filter_by(complaint_id=complaint.complaint_id).count() == 1
        assert ActivityLog.query.filter_by(action="Complaint Submission").count() == 1


def test_citizen_can_view_own_complaint_and_notifications(client, citizen, sample_complaint):
    login(client, citizen.email, citizen.password)

    detail = client.get(f"/citizen/complaints/{sample_complaint.complaint_id}")
    notifications = client.get("/citizen/notifications")

    assert detail.status_code == 200
    assert notifications.status_code == 200
