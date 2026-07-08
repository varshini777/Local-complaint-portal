import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Regexp,
    ValidationError,
)

from backend.models import User


PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$"
)


def validate_password_strength(form, field):
    if not PASSWORD_PATTERN.match(field.data or ""):
        raise ValidationError(
            "Password must include uppercase, lowercase, number, and special character."
        )


class RegistrationForm(FlaskForm):
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
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=150)],
    )
    phone = StringField(
        "Phone",
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
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=72),
            validate_password_strength,
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    security_question = StringField(
        "Security Question",
        validators=[DataRequired(), Length(min=10, max=255)],
    )
    security_answer = StringField(
        "Security Answer",
        validators=[DataRequired(), Length(min=2, max=120)],
    )
    submit = SubmitField("Register")

    def validate_email(self, field):
        existing_user = User.query.filter(
            User.email == field.data.strip().lower()
        ).first()
        if existing_user:
            raise ValidationError("An account with this email already exists.")


class LoginForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=150)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=1, max=72)],
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class ForgotPasswordForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=150)],
    )
    submit = SubmitField("Continue")


class ResetPasswordForm(FlaskForm):
    security_answer = StringField(
        "Security Answer",
        validators=[DataRequired(), Length(min=2, max=120)],
    )
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, max=72),
            validate_password_strength,
        ],
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Reset Password")
