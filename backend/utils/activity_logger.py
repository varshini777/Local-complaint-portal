from flask import request

from backend.extensions import db
from backend.models import ActivityLog


def log_activity(action, user=None, details=None):
    """
    Log an activity to the activity log.
    
    Args:
        action: The action being performed (e.g., "Login", "Complaint Submission")
        user: The user object performing the action (optional)
        details: Additional details about the action (optional)
    """
    try:
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr) if request else None
        log = ActivityLog(
            user_id=user.user_id if user else None,
            action=action,
            ip_address=ip_address,
            details=details,
        )
        db.session.add(log)
    except Exception as e:
        # Silently fail to avoid breaking the main flow
        pass
