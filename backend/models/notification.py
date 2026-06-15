from datetime import datetime

from backend.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    TYPE_COMPLAINT_SUBMITTED = "Complaint Submitted"
    TYPE_COMPLAINT_ASSIGNED = "Complaint Assigned"
    TYPE_STATUS_UPDATED = "Status Updated"
    TYPE_COMPLAINT_RESOLVED = "Complaint Resolved"
    TYPE_COMPLAINT_CLOSED = "Complaint Closed"
    TYPE_SYSTEM = "System"
    TYPES = (
        TYPE_COMPLAINT_SUBMITTED,
        TYPE_COMPLAINT_ASSIGNED,
        TYPE_STATUS_UPDATED,
        TYPE_COMPLAINT_RESOLVED,
        TYPE_COMPLAINT_CLOSED,
        TYPE_SYSTEM,
    )

    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "complaints.complaint_id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        index=True,
    )
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(
        db.Enum(*TYPES, name="notification_type"),
        nullable=False,
        default=TYPE_SYSTEM,
    )
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user = db.relationship(
        "User",
        back_populates="notifications",
    )
    complaint = db.relationship(
        "Complaint",
        back_populates="notifications",
    )

    @property
    def is_unread(self):
        return not self.is_read

    def mark_as_read(self):
        self.is_read = True

    def __repr__(self):
        return f"<Notification {self.notification_id}: {self.notification_type}>"


class Feedback(db.Model):
    __tablename__ = "feedback"

    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "complaints.complaint_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        unique=True,
    )
    citizen_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    rating = db.Column(db.SmallInteger, nullable=False, index=True)
    comment = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    complaint = db.relationship(
        "Complaint",
        back_populates="feedback",
    )
    citizen = db.relationship(
        "User",
        back_populates="feedback_entries",
    )

    @property
    def rating_label(self):
        return f"{self.rating}/5"

    def __repr__(self):
        return f"<Feedback {self.feedback_id}: {self.rating}/5>"
