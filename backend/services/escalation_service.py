from datetime import datetime, timezone, timedelta

from backend.extensions import db
from backend.models import Complaint, SystemSetting


def get_escalation_days():
    """
    Get escalation days from system settings.
    
    Returns:
        tuple: (urgent_days, critical_days)
    """
    urgent_setting = SystemSetting.query.filter_by(setting_key="urgent_escalation_days").first()
    critical_setting = SystemSetting.query.filter_by(setting_key="critical_escalation_days").first()
    
    urgent_days = urgent_setting.typed_value if urgent_setting else 7
    critical_days = critical_setting.typed_value if critical_setting else 15
    
    return urgent_days, critical_days


def check_escalation_required(complaint):
    """
    Check if a complaint needs to be escalated.
    
    Args:
        complaint: The complaint object
    
    Returns:
        str: New escalation level if escalation needed, None otherwise
    """
    if complaint.status in [Complaint.STATUS_RESOLVED, Complaint.STATUS_CLOSED]:
        return None
    
    if complaint.escalation_level == Complaint.ESCALATION_CRITICAL:
        return None
    
    urgent_days, critical_days = get_escalation_days()
    
    if not complaint.submitted_at:
        return None
    
    now_utc = datetime.now(timezone.utc)
    if complaint.submitted_at.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=None)
    days_since_submission = (now_utc - complaint.submitted_at).days
    
    if days_since_submission >= critical_days:
        return Complaint.ESCALATION_CRITICAL
    elif days_since_submission >= urgent_days and complaint.escalation_level == Complaint.ESCALATION_NORMAL:
        return Complaint.ESCALATION_URGENT
    
    return None


def escalate_complaint(complaint, new_level):
    """
    Escalate a complaint to a new level.
    
    Args:
        complaint: The complaint object
        new_level: The new escalation level
    
    Returns:
        bool: True if successful
    """
    if complaint.escalation_level == new_level:
        return False
    
    complaint.escalation_level = new_level
    db.session.add(complaint)
    return True


def check_and_escalate_complaint(complaint):
    """
    Check if a complaint needs escalation and perform it if needed.
    
    Args:
        complaint: The complaint object
    
    Returns:
        tuple: (was_escalated, new_level or None)
    """
    new_level = check_escalation_required(complaint)
    
    if new_level and new_level != complaint.escalation_level:
        escalate_complaint(complaint, new_level)
        return True, new_level
    
    return False, None


def escalate_all_pending_complaints():
    """
    Check and escalate all pending complaints that need escalation.
    
    Returns:
        dict: Statistics about escalation results
    """
    pending_complaints = Complaint.query.filter(
        Complaint.status.notin_([Complaint.STATUS_RESOLVED, Complaint.STATUS_CLOSED]),
        Complaint.is_active == True
    ).all()
    
    escalated_count = 0
    to_urgent = 0
    to_critical = 0
    
    for complaint in pending_complaints:
        was_escalated, new_level = check_and_escalate_complaint(complaint)
        if was_escalated:
            escalated_count += 1
            if new_level == Complaint.ESCALATION_URGENT:
                to_urgent += 1
            elif new_level == Complaint.ESCALATION_CRITICAL:
                to_critical += 1
    
    if escalated_count > 0:
        db.session.commit()
    
    return {
        "total_checked": len(pending_complaints),
        "escalated_count": escalated_count,
        "to_urgent": to_urgent,
        "to_critical": to_critical
    }


def get_escalation_statistics():
    """
    Get statistics about complaint escalation levels.
    
    Returns:
        dict: Escalation statistics
    """
    total = Complaint.query.filter(Complaint.is_active == True).count()
    normal = Complaint.query.filter(
        Complaint.escalation_level == Complaint.ESCALATION_NORMAL,
        Complaint.is_active == True
    ).count()
    urgent = Complaint.query.filter(
        Complaint.escalation_level == Complaint.ESCALATION_URGENT,
        Complaint.is_active == True
    ).count()
    critical = Complaint.query.filter(
        Complaint.escalation_level == Complaint.ESCALATION_CRITICAL,
        Complaint.is_active == True
    ).count()
    
    return {
        "total": total,
        "normal": normal,
        "urgent": urgent,
        "critical": critical,
        "normal_percentage": round((normal / total * 100), 2) if total > 0 else 0,
        "urgent_percentage": round((urgent / total * 100), 2) if total > 0 else 0,
        "critical_percentage": round((critical / total * 100), 2) if total > 0 else 0,
    }
