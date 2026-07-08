from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, Regexp

from backend.models import Complaint


class ComplaintStatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[
            (Complaint.STATUS_IN_PROGRESS, Complaint.STATUS_IN_PROGRESS),
            (Complaint.STATUS_CLOSED, Complaint.STATUS_CLOSED),
        ],
        validators=[DataRequired()],
    )
    remarks = TextAreaField(
        "Remarks",
        validators=[Optional(), Length(max=2000)],
    )
    submit = SubmitField("Update Status")


class ComplaintResolutionForm(FlaskForm):
    resolution_notes = TextAreaField(
        "Resolution Notes",
        validators=[DataRequired(), Length(min=5, max=5000)],
    )
    work_performed = TextAreaField(
        "Work Performed",
        validators=[DataRequired(), Length(max=5000)],
    )
    materials_used = TextAreaField(
        "Materials Used",
        validators=[DataRequired(), Length(max=2000)],
    )
    additional_remarks = TextAreaField(
        "Additional Remarks",
        validators=[DataRequired(), Length(max=2000)],
    )
    after_image = FileField(
        "After Image",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Only image files are allowed."),
            FileSize(max_size=5 * 1024 * 1024, message="Image must be 5 MB or smaller."),
        ],
    )
    submit = SubmitField("Submit Resolution")


class OfficerProfileForm(FlaskForm):
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
    phone = StringField(
        "Phone",
        validators=[
            DataRequired(),
            Length(min=7, max=20),
            Regexp(
                r"^[0-9+\-\s()]+$",
                message="Phone number may contain digits, spaces, +, -, and parentheses.",
            ),
        ],
    )
    submit = SubmitField("Update Profile")


class OfficerChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Current Password",
        validators=[DataRequired(), Length(min=1, max=72)],
    )
    new_password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=8, max=72)],
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Change Password")
