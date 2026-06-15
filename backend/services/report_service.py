from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, case
from backend.extensions import db
from backend.models import Complaint, ComplaintCategory, Ward, User, Feedback
import csv
from io import StringIO


def ensure_utc(dt):
    """Return dt as a UTC-aware datetime.
    Returns None if dt is None.
    Attaches UTC tzinfo if dt is offset-naive.
    Returns dt unchanged if already offset-aware.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def get_dashboard_metrics():
    """Retrieve top-level status counts."""
    base_query = db.session.query(Complaint.status, func.count(Complaint.complaint_id)).filter(Complaint.is_active == True).group_by(Complaint.status).all()
    
    counts = {status: 0 for status in Complaint.STATUSES}
    for status, count in base_query:
        counts[status] = count
        
    total = sum(counts.values())
    
    return {
        "Total Complaints": total,
        "Submitted Complaints": counts.get(Complaint.STATUS_SUBMITTED, 0),
        "Assigned Complaints": counts.get(Complaint.STATUS_ASSIGNED, 0),
        "In Progress Complaints": counts.get(Complaint.STATUS_IN_PROGRESS, 0),
        "Resolved Complaints": counts.get(Complaint.STATUS_RESOLVED, 0),
        "Closed Complaints": counts.get(Complaint.STATUS_CLOSED, 0),
    }


def get_category_analytics():
    """Complaints grouped by Category with count and percentage."""
    results = db.session.query(
        ComplaintCategory.category_name,
        func.count(Complaint.complaint_id)
    ).outerjoin(
        Complaint, (ComplaintCategory.category_id == Complaint.category_id) & (Complaint.is_active == True)
    ).filter(
        ComplaintCategory.is_active == True
    ).group_by(ComplaintCategory.category_name).all()
    
    total_complaints = sum(count for _, count in results)
    
    analytics = []
    for name, count in results:
        percentage = round((count / total_complaints * 100), 2) if total_complaints > 0 else 0.0
        analytics.append({
            "category": name,
            "count": count,
            "percentage": percentage
        })
        
    return analytics


def get_ward_analytics():
    """Complaints grouped by Ward with total, resolved count, and resolution rate."""
    # Using case to sum resolved complaints portably
    results = db.session.query(
        Ward.ward_name,
        func.count(Complaint.complaint_id).label("total"),
        func.sum(case((Complaint.status == Complaint.STATUS_RESOLVED, 1), else_=0)).label("resolved")
    ).outerjoin(
        Complaint, (Ward.ward_id == Complaint.ward_id) & (Complaint.is_active == True)
    ).filter(
        Ward.is_active == True
    ).group_by(Ward.ward_name).all()
    
    analytics = []
    for name, total, resolved in results:
        resolved_count = resolved or 0
        rate = round((resolved_count / total * 100), 2) if total > 0 else 0.0
        analytics.append({
            "ward": name,
            "total_count": total,
            "resolved_count": resolved_count,
            "resolution_rate": rate
        })
        
    return analytics


def get_officer_performance():
    """Per Officer metrics: Assigned, Resolved, Closed, Avg Resolution Time. Using portable Python logic."""
    officers = db.session.query(User).filter(User.role == User.ROLE_OFFICER, User.is_active == True).all()
    
    # Get all active complaints assigned to an officer
    complaints = db.session.query(
        Complaint.assigned_officer_id,
        Complaint.status,
        Complaint.assigned_at,
        Complaint.resolved_at
    ).filter(
        Complaint.assigned_officer_id.isnot(None),
        Complaint.is_active == True
    ).all()
    
    # Group in python to avoid DB-specific timestampdiff
    officer_stats = {o.user_id: {"name": o.full_name, "assigned": 0, "resolved": 0, "closed": 0, "resolution_times": []} for o in officers}
    
    for c in complaints:
        if c.assigned_officer_id in officer_stats:
            stats = officer_stats[c.assigned_officer_id]
            stats["assigned"] += 1
            if c.status == Complaint.STATUS_RESOLVED:
                stats["resolved"] += 1
            elif c.status == Complaint.STATUS_CLOSED:
                stats["closed"] += 1
                
            if c.assigned_at and c.resolved_at:
                aware_assigned = ensure_utc(c.assigned_at)
                aware_resolved = ensure_utc(c.resolved_at)
                delta = aware_resolved - aware_assigned
                stats["resolution_times"].append(delta.total_seconds() / 3600.0)  # hours
                
    analytics = []
    for uid, stats in officer_stats.items():
        avg_time = round(sum(stats["resolution_times"]) / len(stats["resolution_times"]), 2) if stats["resolution_times"] else 0.0
        analytics.append({
            "officer_name": stats["name"],
            "assigned_count": stats["assigned"],
            "resolved_count": stats["resolved"],
            "closed_count": stats["closed"],
            "average_resolution_hours": avg_time
        })
        
    return analytics


def get_escalation_analytics():
    """Counts for Normal, Urgent, Critical escalations."""
    results = db.session.query(Complaint.escalation_level, func.count(Complaint.complaint_id)).filter(Complaint.is_active == True).group_by(Complaint.escalation_level).all()
    
    counts = {level: 0 for level in Complaint.ESCALATION_LEVELS}
    for level, count in results:
        counts[level] = count
        
    return counts


def get_monthly_trends():
    """Monthly submitted, resolved, closed counts for the last 12 months using portable Python grouping."""
    now = datetime.now(timezone.utc)
    one_year_ago = now - relativedelta(months=11)
    
    # Set to beginning of the month 11 months ago
    start_date = datetime(one_year_ago.year, one_year_ago.month, 1, tzinfo=timezone.utc)
    
    complaints = db.session.query(Complaint.submitted_at, Complaint.resolved_at, Complaint.closed_at).filter(
        Complaint.submitted_at >= start_date,
        Complaint.is_active == True
    ).all()
    
    # Initialize buckets for last 12 months
    months = []
    trends = {}
    for i in range(12):
        dt = start_date + relativedelta(months=i)
        key = dt.strftime("%Y-%m")
        months.append(key)
        trends[key] = {"submitted": 0, "resolved": 0, "closed": 0}
        
    for c in complaints:
        if c.submitted_at:
            s_key = c.submitted_at.strftime("%Y-%m")
            if s_key in trends:
                trends[s_key]["submitted"] += 1
                
        if c.resolved_at:
            r_key = c.resolved_at.strftime("%Y-%m")
            if r_key in trends:
                trends[r_key]["resolved"] += 1
                
        if c.closed_at:
            c_key = c.closed_at.strftime("%Y-%m")
            if c_key in trends:
                trends[c_key]["closed"] += 1
                
    analytics = []
    for month in months:
        analytics.append({
            "month": month,
            "submitted": trends[month]["submitted"],
            "resolved": trends[month]["resolved"],
            "closed": trends[month]["closed"]
        })
        
    return analytics


def get_feedback_analytics():
    """Average rating and rating distribution."""
    results = db.session.query(Feedback.rating, func.count(Feedback.feedback_id)).filter(Feedback.is_active == True).group_by(Feedback.rating).all()
    
    distribution = {i: 0 for i in range(1, 6)}
    total_ratings = 0
    sum_ratings = 0
    
    for rating, count in results:
        distribution[rating] = count
        total_ratings += count
        sum_ratings += (rating * count)
        
    average_rating = round((sum_ratings / total_ratings), 2) if total_ratings > 0 else 0.0
    
    return {
        "average_rating": average_rating,
        "distribution": distribution
    }


def get_complaint_aging_analytics():
    """Counts for unresolved complaints grouped by age (0-7, 8-15, 16-30, 30+ days)."""
    unresolved_complaints = db.session.query(Complaint.submitted_at).filter(
        Complaint.status.notin_([Complaint.STATUS_RESOLVED, Complaint.STATUS_CLOSED]),
        Complaint.is_active == True
    ).all()
    
    now = datetime.now(timezone.utc)
    aging = {
        "0-7 days": 0,
        "8-15 days": 0,
        "16-30 days": 0,
        "30+ days": 0
    }
    
    for c in unresolved_complaints:
        if not c.submitted_at:
            continue
        aware_submitted = ensure_utc(c.submitted_at)
        days_old = (now - aware_submitted).days
        if days_old <= 7:
            aging["0-7 days"] += 1
        elif days_old <= 15:
            aging["8-15 days"] += 1
        elif days_old <= 30:
            aging["16-30 days"] += 1
        else:
            aging["30+ days"] += 1
            
    return aging


# CSV Generators

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
    header = ["Complaint Number", "Title", "Category", "Ward", "Status", "Priority", "Escalation Level", "Submitted At"]
    
    def generate_rows():
        # Yield rows in chunks or sequentially to avoid high memory
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
