from datetime import datetime
from uuid import uuid4

from sqlalchemy import event

from backend.extensions import db


class Ward(db.Model):
    __tablename__ = "wards"

    ward_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ward_name = db.Column(db.String(120), nullable=False)
    ward_code = db.Column(db.String(30), nullable=False, unique=True)
    assigned_officer_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.user_id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    assigned_officer = db.relationship(
        "User",
        foreign_keys=[assigned_officer_id],
        back_populates="assigned_wards",
    )
    complaints = db.relationship(
        "Complaint",
        back_populates="ward",
        lazy="dynamic",
    )

    @property
    def display_name(self):
        return f"{self.ward_name} ({self.ward_code})"

    def __repr__(self):
        return f"<Ward {self.ward_id}: {self.ward_code}>"


class ComplaintCategory(db.Model):
    __tablename__ = "complaint_categories"

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    complaints = db.relationship(
        "Complaint",
        back_populates="category",
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<ComplaintCategory {self.category_id}: {self.category_name}>"


class Complaint(db.Model):
    __tablename__ = "complaints"

    STATUS_SUBMITTED = "Submitted"
    STATUS_ASSIGNED = "Assigned"
    STATUS_IN_PROGRESS = "In Progress"
    STATUS_RESOLVED = "Resolved"
    STATUS_CLOSED = "Closed"
    STATUSES = (
        STATUS_SUBMITTED,
        STATUS_ASSIGNED,
        STATUS_IN_PROGRESS,
        STATUS_RESOLVED,
        STATUS_CLOSED,
    )

    PRIORITY_LOW = "Low"
    PRIORITY_MEDIUM = "Medium"
    PRIORITY_HIGH = "High"
    PRIORITY_EMERGENCY = "Emergency"
    PRIORITIES = (
        PRIORITY_LOW,
        PRIORITY_MEDIUM,
        PRIORITY_HIGH,
        PRIORITY_EMERGENCY,
    )

    ESCALATION_NORMAL = "Normal"
    ESCALATION_URGENT = "Urgent"
    ESCALATION_CRITICAL = "Critical"
    ESCALATION_LEVELS = (
        ESCALATION_NORMAL,
        ESCALATION_URGENT,
        ESCALATION_CRITICAL,
    )

    REFILE_AFTER_DAYS = 7

    complaint_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    complaint_number = db.Column(
        db.String(30),
        unique=True,
        nullable=True,
        index=True,
    )
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "complaint_categories.category_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    priority = db.Column(
        db.Enum(*PRIORITIES, name="complaint_priority"),
        nullable=False,
        default=PRIORITY_MEDIUM,
        index=True,
    )
    status = db.Column(
        db.Enum(*STATUSES, name="complaint_status"),
        nullable=False,
        default=STATUS_SUBMITTED,
        index=True,
    )
    escalation_level = db.Column(
        db.Enum(*ESCALATION_LEVELS, name="complaint_escalation_level"),
        nullable=False,
        default=ESCALATION_NORMAL,
        index=True,
    )
    location = db.Column(db.String(255), nullable=False)
    ward_id = db.Column(
        db.Integer,
        db.ForeignKey("wards.ward_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    citizen_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    assigned_officer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id", ondelete="SET NULL", onupdate="CASCADE"),
        index=True,
    )
    before_image_path = db.Column(db.String(255))
    after_image_path = db.Column(db.String(255))
    resolution_notes = db.Column(db.Text)
    work_performed = db.Column(db.Text)
    materials_used = db.Column(db.Text)
    additional_remarks = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    submitted_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    assigned_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    category = db.relationship(
        "ComplaintCategory",
        back_populates="complaints",
    )
    ward = db.relationship(
        "Ward",
        back_populates="complaints",
    )
    citizen = db.relationship(
        "User",
        foreign_keys=[citizen_id],
        back_populates="citizen_complaints",
    )
    assigned_officer = db.relationship(
        "User",
        foreign_keys=[assigned_officer_id],
        back_populates="assigned_complaints",
    )
    updates = db.relationship(
        "ComplaintUpdate",
        back_populates="complaint",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="ComplaintUpdate.created_at.asc()",
    )
    notifications = db.relationship(
        "Notification",
        back_populates="complaint",
        lazy="dynamic",
    )
    feedback = db.relationship(
        "Feedback",
        back_populates="complaint",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def is_pending(self):
        return self.status in {
            self.STATUS_SUBMITTED,
            self.STATUS_ASSIGNED,
            self.STATUS_IN_PROGRESS,
        }

    @property
    def days_since_submitted(self):
        return (datetime.utcnow() - self.submitted_at).days

    @property
    def has_no_progress(self):
        return self.status in {
            self.STATUS_SUBMITTED,
            self.STATUS_ASSIGNED,
        }

    @property
    def needs_refile(self):
        return (
            self.has_no_progress
            and self.days_since_submitted >= self.REFILE_AFTER_DAYS
        )

    @property
    def is_resolved(self):
        return self.status in {self.STATUS_RESOLVED, self.STATUS_CLOSED}

    @property
    def is_closed(self):
        return self.status == self.STATUS_CLOSED

    @property
    def is_escalated(self):
        return self.escalation_level in {
            self.ESCALATION_URGENT,
            self.ESCALATION_CRITICAL,
        }

    @property
    def status_badge_class(self):
        return {
            self.STATUS_SUBMITTED: "secondary",
            self.STATUS_ASSIGNED: "info",
            self.STATUS_IN_PROGRESS: "primary",
            self.STATUS_RESOLVED: "success",
            self.STATUS_CLOSED: "dark",
        }.get(self.status, "secondary")

    @property
    def priority_badge_class(self):
        return {
            self.PRIORITY_LOW: "success",
            self.PRIORITY_MEDIUM: "info",
            self.PRIORITY_HIGH: "warning",
            self.PRIORITY_EMERGENCY: "danger",
        }.get(self.priority, "secondary")

    @property
    def timeline(self):
        return self.updates.order_by(ComplaintUpdate.created_at.asc()).all()

    @property
    def has_before_image(self):
        return bool(self.before_image_path)

    @property
    def has_after_image(self):
        return bool(self.after_image_path)

    @property
    def has_resolution(self):
        return any(
            (
                self.resolution_notes,
                self.work_performed,
                self.materials_used,
                self.additional_remarks,
            )
        )

    def assign_complaint_number(self):
        current_year = datetime.utcnow().year
        self.complaint_number = f"LCP-{current_year}-{self.complaint_id:06d}"
        return self.complaint_number

    def __repr__(self):
        return f"<Complaint {self.complaint_id}: {self.title}>"


@event.listens_for(Complaint, "after_insert")
def set_final_complaint_number(mapper, connection, target):
    target.assign_complaint_number()
    connection.execute(
        Complaint.__table__.update()
        .where(Complaint.complaint_id == target.complaint_id)
        .values(complaint_number=target.complaint_number)
    )


class ComplaintUpdate(db.Model):
    __tablename__ = "complaint_updates"

    update_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "complaints.complaint_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    updated_by = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id", ondelete="SET NULL", onupdate="CASCADE"),
        index=True,
    )
    status = db.Column(
        db.Enum(*Complaint.STATUSES, name="complaint_update_status"),
        nullable=False,
        index=True,
    )
    action = db.Column(db.String(120), nullable=False)
    remarks = db.Column(db.Text)
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

    complaint = db.relationship(
        "Complaint",
        back_populates="updates",
    )
    updated_by_user = db.relationship(
        "User",
        back_populates="complaint_updates",
    )

    @property
    def actor_name(self):
        if self.updated_by_user:
            return self.updated_by_user.full_name
        return "System"

    def __repr__(self):
        return f"<ComplaintUpdate {self.update_id}: {self.action}>"
