from datetime import datetime

from backend.extensions import db


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id", ondelete="SET NULL", onupdate="CASCADE"),
        index=True,
    )
    action = db.Column(db.String(150), nullable=False, index=True)
    ip_address = db.Column(db.String(45))
    details = db.Column(db.Text)
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
        back_populates="activity_logs",
    )

    @property
    def actor_name(self):
        if self.user:
            return self.user.full_name
        return "System"

    def __repr__(self):
        return f"<ActivityLog {self.log_id}: {self.action}>"


class SystemSetting(db.Model):
    __tablename__ = "system_settings"

    TYPE_STRING = "string"
    TYPE_INTEGER = "integer"
    TYPE_DECIMAL = "decimal"
    TYPE_BOOLEAN = "boolean"
    TYPES = (TYPE_STRING, TYPE_INTEGER, TYPE_DECIMAL, TYPE_BOOLEAN)

    setting_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    setting_key = db.Column(db.String(100), nullable=False, unique=True)
    setting_value = db.Column(db.String(255), nullable=False)
    setting_type = db.Column(
        db.Enum(*TYPES, name="system_setting_type"),
        nullable=False,
        default=TYPE_STRING,
    )
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    @property
    def typed_value(self):
        if self.setting_type == self.TYPE_INTEGER:
            return int(self.setting_value)
        if self.setting_type == self.TYPE_DECIMAL:
            return float(self.setting_value)
        if self.setting_type == self.TYPE_BOOLEAN:
            return self.setting_value.strip().lower() in {"1", "true", "yes", "on"}
        return self.setting_value

    def __repr__(self):
        return f"<SystemSetting {self.setting_key}={self.setting_value}>"
