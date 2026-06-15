# DEPRECATED: This file is kept for backward compatibility.
# Please import from backend.models instead.
# Example: from backend.models import User, Complaint, etc.

from backend.models import (
    ActivityLog,
    Complaint,
    ComplaintCategory,
    ComplaintUpdate,
    Feedback,
    Notification,
    SystemSetting,
    User,
    Ward,
)

__all__ = [
    "User",
    "Complaint",
    "ComplaintCategory",
    "Ward",
    "ComplaintUpdate",
    "Notification",
    "Feedback",
    "ActivityLog",
    "SystemSetting",
]
