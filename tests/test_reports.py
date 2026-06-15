from tests.conftest import login


def test_report_dashboard_loads(client):
    login(client, "admin@localportal.com", "Admin@123")

    response = client.get("/admin/reports/")

    assert response.status_code == 200
    assert b"Reports Dashboard" in response.data


def test_csv_exports_load(client):
    login(client, "admin@localportal.com", "Admin@123")

    complaint_export = client.get("/admin/reports/export/complaints")
    officer_export = client.get("/admin/reports/export/officers")
    feedback_export = client.get("/admin/reports/export/feedback")

    assert complaint_export.status_code == 200
    assert officer_export.status_code == 200
    assert feedback_export.status_code == 200
    assert complaint_export.mimetype == "text/csv"
    assert officer_export.mimetype == "text/csv"
    assert feedback_export.mimetype == "text/csv"
