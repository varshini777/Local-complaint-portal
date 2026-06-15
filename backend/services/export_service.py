import csv
from io import StringIO

from backend.extensions import db
from backend.models import Complaint, User, Feedback


def generate_csv_stream(header, rows_iterable):
    """Yields CSV formatted lines. Used for streaming responses."""
    data = StringIO()
    writer = csv.writer(data)
    
    # Write header
    writer.writerow(header)
    yield data.getvalue().encode('utf-8')
    data.seek(0)
    data.truncate(0)
    
    # Write rows
    for row in rows_iterable:
        writer.writerow(row)
        yield data.getvalue().encode('utf-8')
        data.seek(0)
        data.truncate(0)


def export_complaints_csv():
    """Generate CSV export of all complaints."""
    header = ["Complaint Number", "Title", "Category", "Ward", "Status", "Priority", "Escalation Level", "Submitted At"]
    
    def generate_rows():
        complaints = db.session.query(Complaint).filter(Complaint.is_active == True).order_by(Complaint.submitted_at.desc()).yield_per(100)
        for c in complaints:
            yield [
                c.complaint_number,
                c.title,
                c.category.category_name if c.category else "N/A",
                c.ward.ward_name if c.ward else "N/A",
                c.status,
                c.priority,
                c.escalation_level,
                c.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if c.submitted_at else ""
            ]
            
    return generate_csv_stream(header, generate_rows())


def export_officer_performance_csv():
    """Generate CSV export of officer performance metrics."""
    from backend.services.analytics_service import get_officer_performance
    
    header = ["Officer Name", "Assigned", "Resolved", "Closed", "Avg Resolution Hours"]
    
    def generate_rows():
        performance = get_officer_performance()
        for p in performance:
            yield [
                p["officer_name"],
                p["assigned_count"],
                p["resolved_count"],
                p["closed_count"],
                p["average_resolution_hours"]
            ]
            
    return generate_csv_stream(header, generate_rows())


def export_feedback_csv():
    """Generate CSV export of feedback entries."""
    header = ["Complaint Number", "Rating", "Comment", "Citizen", "Submitted At"]
    
    def generate_rows():
        feedback_entries = db.session.query(Feedback).filter(Feedback.is_active == True).order_by(Feedback.created_at.desc()).yield_per(100)
        for f in feedback_entries:
            yield [
                f.complaint.complaint_number if f.complaint else "N/A",
                f.rating,
                f.comment or "",
                f.citizen.full_name if f.citizen else "N/A",
                f.created_at.strftime("%Y-%m-%d %H:%M:%S") if f.created_at else ""
            ]
            
    return generate_csv_stream(header, generate_rows())


def export_users_csv():
    """Generate CSV export of all users."""
    header = ["User ID", "Full Name", "Email", "Phone", "Role", "Is Active", "Created At"]
    
    def generate_rows():
        users = db.session.query(User).order_by(User.created_at.desc()).yield_per(100)
        for u in users:
            yield [
                u.user_id,
                u.full_name,
                u.email,
                u.phone or "",
                u.role,
                "Yes" if u.is_active else "No",
                u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else ""
            ]
            
    return generate_csv_stream(header, generate_rows())


def export_wards_csv():
    """Generate CSV export of all wards."""
    from backend.models import Ward
    
    header = ["Ward ID", "Ward Name", "Ward Code", "Assigned Officer", "Is Active", "Created At"]
    
    def generate_rows():
        wards = db.session.query(Ward).order_by(Ward.ward_name).yield_per(100)
        for w in wards:
            yield [
                w.ward_id,
                w.ward_name,
                w.ward_code,
                w.assigned_officer.full_name if w.assigned_officer else "Unassigned",
                "Yes" if w.is_active else "No",
                w.created_at.strftime("%Y-%m-%d %H:%M:%S") if w.created_at else ""
            ]
            
    return generate_csv_stream(header, generate_rows())
