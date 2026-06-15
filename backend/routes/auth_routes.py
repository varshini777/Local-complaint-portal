from functools import wraps

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.routing import BuildError

from backend.extensions import db, limiter
from backend.forms.auth_forms import (
    ForgotPasswordForm,
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
)
from backend.models import User
from backend.services.activity_log_service import log_activity
from backend.services.auth_service import (
    authenticate_user,
    check_user_exists,
    clear_password_reset_session,
    initiate_password_reset,
    validate_password_reset_session,
)


auth_bp = Blueprint("auth", __name__)


def safe_redirect(endpoint, fallback="index"):
    try:
        return redirect(url_for(endpoint))
    except BuildError:
        return redirect(url_for(fallback))


def redirect_for_role(user):
    # Redirect all users to home page instead of role-specific dashboards
    return safe_redirect("index")


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(*args, **kwargs):
            if not current_user.is_active or current_user.role != required_role:
                flash("Access denied. You do not have permission to view this page.", "danger")
                return redirect_for_role(current_user)
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator


admin_required = role_required(User.ROLE_ADMIN)
officer_required = role_required(User.ROLE_OFFICER)
citizen_required = role_required(User.ROLE_CITIZEN)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect_for_role(current_user)

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip(),
            role=User.ROLE_CITIZEN,
            security_question=form.security_question.data.strip(),
            is_active=True,
        )
        user.set_password(form.password.data)
        user.set_security_answer(form.security_answer.data)

        try:
            db.session.add(user)
            db.session.flush()
            try:
                log_activity("Citizen Registration", user, "New citizen account created.")
            except Exception as e:
                app.logger.error(f"Activity logging failed during registration: {e}")
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Registration failed: {e}")
            flash("Registration failed. Please try again.", "danger")

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect_for_role(current_user)

    form = LoginForm()

    if form.validate_on_submit():
        user = authenticate_user(form.email.data, form.password.data)

        if user:
            login_user(
                user,
                remember=form.remember_me.data,
            )
            try:
                log_activity("Login", user, "User logged in successfully.")
                db.session.commit()
            except SQLAlchemyError:
                db.session.rollback()
            flash("Login successful.", "success")
            return redirect_for_role(user)

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    user = current_user._get_current_object()

    try:
        log_activity("Logout", user, "User logged out.")
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()

    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("3 per hour")
def forgot_password():
    if current_user.is_authenticated:
        return redirect_for_role(current_user)

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = check_user_exists(form.email.data)

        if user and initiate_password_reset(user):
            flash("Answer your security question to reset your password.", "info")
            return redirect(url_for("auth.reset_password"))

        flash("No active account with password reset details was found.", "warning")

    return render_template("auth/forgot_password.html", form=form)


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect_for_role(current_user)

    is_valid, user_id, error_message = validate_password_reset_session()

    if not is_valid:
        flash(error_message, "warning")
        return redirect(url_for("auth.forgot_password"))

    user = db.session.get(User, user_id)

    form = ResetPasswordForm()

    if form.validate_on_submit():
        if not user.check_security_answer(form.security_answer.data):
            flash("Security answer is incorrect.", "danger")
            return render_template("auth/reset_password.html", form=form, user=user)

        user.set_password(form.password.data)

        try:
            log_activity("Password Reset", user, "Password reset using security question.")
            db.session.commit()
            clear_password_reset_session()
            flash("Password reset successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("Password reset failed. Please try again.", "danger")

    return render_template("auth/reset_password.html", form=form, user=user)
