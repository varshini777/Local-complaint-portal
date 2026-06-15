from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, Regexp

from backend.models import Complaint


class ComplaintForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[DataRequired(), Length(min=5, max=200)],
    )
    description = TextAreaField(
        "Description",
        validators=[DataRequired(), Length(min=10, max=5000)],
    )
    category = SelectField(
        "Category",
        coerce=int,
        validators=[DataRequired()],
    )
    priority = SelectField(
        "Priority",
        choices=[(priority, priority) for priority in Complaint.PRIORITIES],
        validators=[DataRequired()],
    )
    location = StringField(
        "Location",
        validators=[DataRequired(), Length(min=3, max=255)],
    )
    ward = SelectField(
        "Ward",
        coerce=int,
        validators=[DataRequired()],
    )
    before_image = FileField(
        "Before Image",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Only image files are allowed."),
            FileSize(max_size=5 * 1024 * 1024, message="Image must be 5 MB or smaller."),
        ],
    )
    submit = SubmitField("Submit Complaint")


class ProfileUpdateForm(FlaskForm):
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


class ChangePasswordForm(FlaskForm):
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


class FeedbackForm(FlaskForm):
    rating = SelectField(
        "Rating",
        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
        coerce=int,
        validators=[DataRequired()],
    )
    comment = TextAreaField(
        "Comment",
        validators=[Optional(), Length(max=1000)],
    )
    submit = SubmitField("Submit Feedback")
