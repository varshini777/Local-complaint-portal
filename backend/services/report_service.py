from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, case
from backend.extensions import db
from backend.models import Complaint, ComplaintCategory, Ward, User, Feedback
from backend.utils.datetime_utils import utc_to_ist
import csv
from io import StringIO


def ensure_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def get_dashboard_metrics():
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
        if count == 0:
            continue
        percentage = round((count / total_complaints * 100), 2) if total_complaints > 0 else 0.0
        analytics.append({
            "category": name,
            "count": count,
            "percentage": percentage
        })
    return analytics


def get_ward_analytics():
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
    officers = db.session.query(User).filter(User.role == User.ROLE_OFFICER, User.is_active == True).all()
    
    complaints = db.session.query(
        Complaint.assigned_officer_id,
        Complaint.status,
        Complaint.escalation_level,
        Complaint.assigned_at,
        Complaint.resolved_at
    ).filter(
        Complaint.assigned_officer_id.isnot(None),
        Complaint.is_active == True
    ).all()
    
    feedbacks = db.session.query(
        Complaint.assigned_officer_id,
        func.avg(Feedback.rating)
    ).join(Feedback, Complaint.complaint_id == Feedback.complaint_id).filter(
        Complaint.assigned_officer_id.isnot(None),
        Feedback.is_active == True
    ).group_by(Complaint.assigned_officer_id).all()
    
    feedback_dict = {f[0]: float(f[1]) for f in feedbacks}
    
    officer_stats = {o.user_id: {"name": o.full_name, "assigned": 0, "pending": 0, "resolved": 0, "closed": 0, "escalated": 0, "resolution_times": []} for o in officers}
    
    for c in complaints:
        if c.assigned_officer_id in officer_stats:
            stats = officer_stats[c.assigned_officer_id]
            stats["assigned"] += 1
            if c.status in [Complaint.STATUS_ASSIGNED, Complaint.STATUS_IN_PROGRESS]:
                stats["pending"] += 1
            if c.status == Complaint.STATUS_RESOLVED:
                stats["resolved"] += 1
            elif c.status == Complaint.STATUS_CLOSED:
                stats["closed"] += 1
            if c.escalation_level != Complaint.ESCALATION_NORMAL:
                stats["escalated"] += 1
                
            if c.assigned_at and c.resolved_at:
                aware_assigned = ensure_utc(c.assigned_at)
                aware_resolved = ensure_utc(c.resolved_at)
                delta = aware_resolved - aware_assigned
                stats["resolution_times"].append(delta.total_seconds() / 3600.0)
                
    analytics = []
    for uid, stats in officer_stats.items():
        avg_time = round(sum(stats["resolution_times"]) / len(stats["resolution_times"]), 2) if stats["resolution_times"] else 0.0
        rating = round(feedback_dict.get(uid, 0.0), 1)
        res_pct = round((stats["resolved"] + stats["closed"]) / stats["assigned"] * 100, 2) if stats["assigned"] > 0 else 0.0
        
        if stats["assigned"] == 0:
            badge = "N/A"
        elif res_pct >= 80:
            badge = "Excellent"
        elif res_pct >= 50:
            badge = "Good"
        elif res_pct < 30 or stats["escalated"] > 5:
            badge = "Needs Attention"
        else:
            badge = "Average"
            
        analytics.append({
            "officer_name": stats["name"],
            "assigned_count": stats["assigned"],
            "pending_count": stats["pending"],
            "resolved_count": stats["resolved"],
            "closed_count": stats["closed"],
            "escalated_count": stats["escalated"],
            "resolution_percentage": res_pct,
            "average_resolution_hours": avg_time,
            "citizen_rating": rating,
            "badge": badge
        })
        
    return analytics


def get_escalation_analytics():
    results = db.session.query(Complaint.escalation_level, func.count(Complaint.complaint_id)).filter(Complaint.is_active == True).group_by(Complaint.escalation_level).all()
    counts = {level: 0 for level in Complaint.ESCALATION_LEVELS}
    for level, count in results:
        counts[level] = count
    return counts


def get_monthly_trends():
    now = datetime.now(timezone.utc)
    one_year_ago = now - relativedelta(months=11)
    start_date = datetime(one_year_ago.year, one_year_ago.month, 1, tzinfo=timezone.utc)
    
    complaints = db.session.query(Complaint.submitted_at, Complaint.resolved_at, Complaint.closed_at).filter(
        Complaint.submitted_at >= start_date,
        Complaint.is_active == True
    ).all()
    
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
    unresolved_complaints = db.session.query(Complaint.submitted_at).filter(
        Complaint.status.notin_([Complaint.STATUS_RESOLVED, Complaint.STATUS_CLOSED]),
        Complaint.is_active == True
    ).all()
    
    now = datetime.now(timezone.utc)
    aging = {
        "Today": 0,
        "1-3 Days": 0,
        "4-7 Days": 0,
        "8-15 Days": 0,
        "16-30 Days": 0,
        "Over 30 Days": 0
    }
    
    for c in unresolved_complaints:
        if not c.submitted_at:
            continue
        aware_submitted = ensure_utc(c.submitted_at)
        days_old = (now - aware_submitted).days
        
        if days_old == 0:
            aging["Today"] += 1
        elif days_old <= 3:
            aging["1-3 Days"] += 1
        elif days_old <= 7:
            aging["4-7 Days"] += 1
        elif days_old <= 15:
            aging["8-15 Days"] += 1
        elif days_old <= 30:
            aging["16-30 Days"] += 1
        else:
            aging["Over 30 Days"] += 1
            
    return aging


def generate_csv_stream(header, rows_iterable):
    data = StringIO()
    writer = csv.writer(data)
    writer.writerow(header)
    yield data.getvalue().encode('utf-8')
    data.seek(0)
    data.truncate(0)
    for row in rows_iterable:
        writer.writerow(row)
        yield data.getvalue().encode('utf-8')
        data.seek(0)
        data.truncate(0)


def format_dt_ist(dt):
    if not dt:
        return ""
    aware_dt = ensure_utc(dt)
    ist_dt = utc_to_ist(aware_dt)
    if isinstance(ist_dt, str):
        return ist_dt # fallback
    return ist_dt.strftime("%Y-%m-%d %I:%M %p")


def export_complaints_csv():
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
                format_dt_ist(c.submitted_at)
            ]
    return generate_csv_stream(header, generate_rows())


def export_officer_performance_csv():
    header = ["Officer Name", "Assigned", "Pending", "Resolved", "Closed", "Escalated", "Resolution %", "Avg Res Hours", "Rating", "Badge"]
    def generate_rows():
        performance = get_officer_performance()
        for p in performance:
            yield [
                p["officer_name"],
                p["assigned_count"],
                p["pending_count"],
                p["resolved_count"],
                p["closed_count"],
                p["escalated_count"],
                f"{p['resolution_percentage']}%",
                p["average_resolution_hours"],
                p["citizen_rating"],
                p["badge"]
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
                format_dt_ist(f.created_at)
            ]
    return generate_csv_stream(header, generate_rows())
