from datetime import datetime, timezone
from backend.extensions import db
from backend.models import Notification, ActivityLog, User

def create_notification(user_id, complaint_id, message, notification_type):
    """
    Creates a Notification object and adds it to the session.
    Avoids duplicating unread notifications of the same type for the same complaint and user.
    """
    user = db.session.get(User, user_id)
    if not user or not user.is_active:
        return None

    existing_notification = Notification.query.filter_by(
        user_id=user_id,
        complaint_id=complaint_id,
        notification_type=notification_type,
        is_read=False,
        is_active=True
    ).first()
    
    if existing_notification:
        return existing_notification
        
    notification = Notification(
        user_id=user_id,
        complaint_id=complaint_id,
        message=message,
        notification_type=notification_type,
        created_at=datetime.now(timezone.utc)
    )
    db.session.add(notification)
    return notification


def create_complaint_submitted_notification(complaint, user_id):
    return create_notification(
        user_id=user_id,
        complaint_id=complaint.complaint_id,
        message=f"Complaint {complaint.complaint_number} submitted successfully.",
        notification_type=Notification.TYPE_COMPLAINT_SUBMITTED
    )


def create_complaint_assigned_notification(complaint, officer_id):
    return create_notification(
        user_id=officer_id,
        complaint_id=complaint.complaint_id,
        message=f"You have been assigned to complaint {complaint.complaint_number}.",
        notification_type=Notification.TYPE_COMPLAINT_ASSIGNED
    )


def create_complaint_status_notification(complaint, citizen_id, old_status):
    return create_notification(
        user_id=citizen_id,
        complaint_id=complaint.complaint_id,
        message=f"Complaint {complaint.complaint_number} status changed from {old_status} to {complaint.status}.",
        notification_type=Notification.TYPE_STATUS_UPDATED
    )


def create_complaint_resolved_notification(complaint, citizen_id):
    return create_notification(
        user_id=citizen_id,
        complaint_id=complaint.complaint_id,
        message=f"Complaint {complaint.complaint_number} has been resolved.",
        notification_type=Notification.TYPE_COMPLAINT_RESOLVED
    )


def create_complaint_closed_notification(complaint, citizen_id):
    return create_notification(
        user_id=citizen_id,
        complaint_id=complaint.complaint_id,
        message=f"Your complaint {complaint.complaint_number} has been closed by an administrator.",
        notification_type=Notification.TYPE_COMPLAINT_CLOSED
    )


def mark_notification_read(notification_id, user_id):
    notification = Notification.query.filter(
        Notification.notification_id == notification_id,
        Notification.user_id == user_id,
        Notification.is_active.is_(True)
    ).first()
    
    if not notification:
        return None
        
    notification.mark_as_read()
    db.session.commit()
    return notification


def mark_all_notifications_read(user_id):
    updated_count = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.is_active.is_(True),
        Notification.is_read.is_(False),
    ).update(
        {Notification.is_read: True},
        synchronize_session=False,
    )
    
    if updated_count > 0:
        db.session.commit()
        
    return updated_count
