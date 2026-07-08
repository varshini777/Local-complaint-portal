from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, Regexp, ValidationError

from backend.models import User, Ward, Complaint, ComplaintCategory


from backend.forms.auth_forms import validate_password_strength

def optional_password_strength(form, field):
    if field.data:
        validate_password_strength(form, field)

class AdminUserSearchForm(FlaskForm):
    search_term = StringField("Search", validators=[Optional(), Length(max=100)])
    role = SelectField(
        "Role",
        choices=[("", "All Roles"), (User.ROLE_CITIZEN, "Citizen"), (User.ROLE_OFFICER, "Officer"), (User.ROLE_ADMIN, "Admin")],
        validators=[Optional()],
    )
    submit = SubmitField("Search")


class AdminOfficerForm(FlaskForm):
    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=2, max=120),
            Regexp(
                r"^[A-Za-z][A-Za-z\s.'-]*$",
                message="Full name may contain letters, spaces, dots, apostrophes, and hyphens.",
            ),
        ],
    )
    email = StringField(
        "Email Address",
        validators=[DataRequired(), Email(), Length(max=150)],
    )
    phone = StringField(
        "Phone Number",
        validators=[
            DataRequired(),
            Length(min=10, max=10, message="Phone number must be exactly 10 digits."),
            Regexp(
                r"^\d{10}$",
                message="Phone number must contain exactly 10 digits.",
            ),
        ],
    )
    password = PasswordField(
        "Password (leave blank to keep current if editing)",
        validators=[Optional(), Length(min=8, max=72), optional_password_strength],
    )
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Officer")


class AdminWardForm(FlaskForm):
    ward_name = StringField("Ward Name", validators=[DataRequired(), Length(max=120)])
    ward_code = StringField("Ward Code", validators=[DataRequired(), Length(max=30)])
    assigned_officer_id = SelectField("Assigned Officer", coerce=int, validators=[Optional()])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Ward")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        officers = User.query.filter_by(role=User.ROLE_OFFICER, is_active=True).order_by(User.full_name).all()
        self.assigned_officer_id.choices = [(0, "Unassigned")] + [(o.user_id, o.full_name) for o in officers]

    def validate_assigned_officer_id(self, field):
        if field.data == 0:
            field.data = None


class AdminComplaintAssignForm(FlaskForm):
    assigned_officer_id = SelectField("Assign Officer", coerce=int, validators=[Optional()])
    submit = SubmitField("Assign Complaint")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        officers = User.query.filter_by(role=User.ROLE_OFFICER, is_active=True).order_by(User.full_name).all()
        self.assigned_officer_id.choices = [(0, "Unassigned")] + [(o.user_id, o.full_name) for o in officers]

    def validate_assigned_officer_id(self, field):
        if field.data == 0:
            field.data = None


class AdminComplaintFilterForm(FlaskForm):
    search_term = StringField("Search (ID, Title)", validators=[Optional(), Length(max=100)])
    status = SelectField(
        "Status",
        choices=[
            ("", "All Statuses"),
            ("Submitted", "Submitted"),
            ("Assigned", "Assigned"),
            ("In Progress", "In Progress"),
            ("Resolved", "Resolved"),
            ("Closed", "Closed"),
        ],
        validators=[Optional()],
    )
    priority = SelectField(
        "Priority",
        choices=[("", "All Priorities"), (Complaint.PRIORITY_LOW, "Low"), (Complaint.PRIORITY_MEDIUM, "Medium"), (Complaint.PRIORITY_HIGH, "High"), (Complaint.PRIORITY_EMERGENCY, "Emergency")],
        validators=[Optional()]
    )
    category_id = SelectField("Category", coerce=int, validators=[Optional()])
    ward_id = SelectField("Ward", coerce=int, validators=[Optional()])
    officer_id = SelectField("Officer", coerce=int, validators=[Optional()])
    submit = SubmitField("Filter")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = ComplaintCategory.query.order_by(ComplaintCategory.category_name).all()
        self.category_id.choices = [(0, "All Categories")] + [(c.category_id, c.category_name) for c in categories]
        
        wards = Ward.query.order_by(Ward.ward_name).all()
        self.ward_id.choices = [(0, "All Wards")] + [(w.ward_id, w.ward_name) for w in wards]
        
        officers = User.query.filter_by(role=User.ROLE_OFFICER, is_active=True).order_by(User.full_name).all()
        self.officer_id.choices = [(0, "All Officers"), (-1, "Unassigned")] + [(o.user_id, o.full_name) for o in officers]

    def validate_category_id(self, field):
        if field.data == 0:
            field.data = None

    def validate_ward_id(self, field):
        if field.data == 0:
            field.data = None
            
    def validate_officer_id(self, field):
        if field.data == 0:
            field.data = None


class AdminSystemSettingsForm(FlaskForm):
    urgent_escalation_days = IntegerField(
        "Urgent Escalation Days", validators=[DataRequired(), NumberRange(min=1, max=30)]
    )
    critical_escalation_days = IntegerField(
        "Critical Escalation Days", validators=[DataRequired(), NumberRange(min=1, max=60)]
    )
    max_upload_size_mb = IntegerField(
        "Max Upload Size (MB)", validators=[DataRequired(), NumberRange(min=1, max=50)]
    )
    submit = SubmitField("Save Settings")


class AdminActivityLogFilterForm(FlaskForm):
    user_id = SelectField("User", coerce=int, validators=[Optional()])
    action = StringField("Action", validators=[Optional(), Length(max=150)])
    date = DateField("Date", format="%Y-%m-%d", validators=[Optional()])
    submit = SubmitField("Filter")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        users = User.query.order_by(User.full_name).all()
        self.user_id.choices = [(0, "All Users")] + [(u.user_id, f"{u.full_name} ({u.role})") for u in users]

    def validate_user_id(self, field):
        if field.data == 0:
            field.data = None
