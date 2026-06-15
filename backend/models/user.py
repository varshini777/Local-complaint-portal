from datetime import datetime

import bcrypt
from flask_login import UserMixin

from backend.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    ROLE_CITIZEN = "citizen"
    ROLE_OFFICER = "officer"
    ROLE_ADMIN = "admin"
    ROLES = (ROLE_CITIZEN, ROLE_OFFICER, ROLE_ADMIN)

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(
        db.Enum(*ROLES, name="user_role"),
        nullable=False,
        default=ROLE_CITIZEN,
        index=True,
    )
    security_question = db.Column(db.String(255))
    security_answer_hash = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    citizen_complaints = db.relationship(
        "Complaint",
        foreign_keys="Complaint.citizen_id",
        back_populates="citizen",
        lazy="dynamic",
    )
    assigned_complaints = db.relationship(
        "Complaint",
        foreign_keys="Complaint.assigned_officer_id",
        back_populates="assigned_officer",
        lazy="dynamic",
    )
    assigned_wards = db.relationship(
        "Ward",
        foreign_keys="Ward.assigned_officer_id",
        back_populates="assigned_officer",
        lazy="dynamic",
    )
    complaint_updates = db.relationship(
        "ComplaintUpdate",
        back_populates="updated_by_user",
        lazy="dynamic",
    )
    notifications = db.relationship(
        "Notification",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    feedback_entries = db.relationship(
        "Feedback",
        back_populates="citizen",
        lazy="dynamic",
    )
    activity_logs = db.relationship(
        "ActivityLog",
        back_populates="user",
        lazy="dynamic",
    )

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        password_bytes = password.encode("utf-8")
        self.password_hash = bcrypt.hashpw(
            password_bytes,
            bcrypt.gensalt(),
        ).decode("utf-8")

    def check_password(self, password):
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password_hash.encode("utf-8"),
        )

    def set_security_answer(self, answer):
        answer_bytes = answer.strip().lower().encode("utf-8")
        self.security_answer_hash = bcrypt.hashpw(
            answer_bytes,
            bcrypt.gensalt(),
        ).decode("utf-8")

    def check_security_answer(self, answer):
        if not self.security_answer_hash:
            return False
        return bcrypt.checkpw(
            answer.strip().lower().encode("utf-8"),
            self.security_answer_hash.encode("utf-8"),
        )

    @property
    def is_citizen(self):
        return self.role == self.ROLE_CITIZEN

    @property
    def is_officer(self):
        return self.role == self.ROLE_OFFICER

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def role_label(self):
        return self.role.title()

    def __repr__(self):
        return f"<User {self.user_id}: {self.email}>"
