from flask import request
from sqlalchemy.exc import SQLAlchemyError

from backend.extensions import db
from backend.models import ActivityLog


def log_activity(action, user=None, details=None):
    """
    Log an activity to the activity log.
    
    Args:
        action: The action being performed (e.g., "Login", "Complaint Submission")
        user: The user object performing the action (optional)
        details: Additional details about the action (optional)
    
    Returns:
        ActivityLog object (added to session but not committed)
    """
    log = ActivityLog(
        user_id=user.user_id if user else None,
        action=action,
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        details=details,
    )
    db.session.add(log)
    return log


def log_activity_with_commit(action, user=None, details=None):
    """
    Log an activity and commit the session.
    
    Args:
        action: The action being performed
        user: The user object performing the action (optional)
        details: Additional details about the action (optional)
    
    Returns:
        bool: True if successful, False if failed
    """
    try:
        log_activity(action, user, details)
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        return False


def get_user_activity_logs(user_id, limit=50):
    """
    Get activity logs for a specific user.
    
    Args:
        user_id: The user ID to get logs for
        limit: Maximum number of logs to return
    
    Returns:
        List of ActivityLog objects
    """
    return ActivityLog.query.filter_by(user_id=user_id).order_by(
        ActivityLog.created_at.desc()
    ).limit(limit).all()


def get_recent_activity_logs(limit=100):
    """
    Get recent activity logs across all users.
    
    Args:
        limit: Maximum number of logs to return
    
    Returns:
        List of ActivityLog objects
    """
    return ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
