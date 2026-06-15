from datetime import datetime, timezone, timedelta
from flask import session

from backend.extensions import db
from backend.models import User


def validate_password_strength(password):
    """
    Validate password strength requirements.
    
    Args:
        password: The password to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if len(password) > 72:
        return False, "Password must not exceed 72 characters."
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    if not (has_upper and has_lower and has_digit and has_special):
        return False, "Password must include uppercase, lowercase, number, and special character."
    
    return True, None


def initiate_password_reset(user):
    """
    Initiate password reset process for a user.
    
    Args:
        user: The user object
    
    Returns:
        bool: True if successful
    """
    if not user or not user.security_question or not user.security_answer_hash:
        return False
    
    session["password_reset_user_id"] = user.user_id
    session["password_reset_expires"] = (
        datetime.now(timezone.utc) + timedelta(minutes=15)
    ).isoformat()
    
    return True


def validate_password_reset_session():
    """
    Validate that the password reset session is still valid.
    
    Returns:
        tuple: (is_valid, user_id or None, error_message or None)
    """
    user_id = session.get("password_reset_user_id")
    expires_at = session.get("password_reset_expires")
    
    if not user_id or not expires_at:
        return False, None, "Please enter your email to start password reset."
    
    try:
        reset_expires_at = datetime.fromisoformat(expires_at)
    except ValueError:
        return False, None, "Invalid session. Please try again."
    
    if datetime.now(timezone.utc) > reset_expires_at:
        session.pop("password_reset_user_id", None)
        session.pop("password_reset_expires", None)
        return False, None, "Password reset session expired. Please try again."
    
    user = db.session.get(User, int(user_id))
    if not user or not user.is_active:
        session.pop("password_reset_user_id", None)
        session.pop("password_reset_expires", None)
        return False, None, "Password reset session expired. Please try again."
    
    return True, user_id, None


def clear_password_reset_session():
    """Clear the password reset session."""
    session.pop("password_reset_user_id", None)
    session.pop("password_reset_expires", None)


def check_user_exists(email):
    """
    Check if a user with the given email exists.
    
    Args:
        email: The email to check
    
    Returns:
        User object or None
    """
    return User.query.filter(
        User.email == email.strip().lower(),
        User.is_active.is_(True),
    ).first()


def authenticate_user(email, password):
    """
    Authenticate a user with email and password.
    
    Args:
        email: The user's email
        password: The user's password
    
    Returns:
        User object if successful, None otherwise
    """
    user = User.query.filter(User.email == email.strip().lower()).first()
    
    if user and user.is_active and user.check_password(password):
        return user
    
    return None
