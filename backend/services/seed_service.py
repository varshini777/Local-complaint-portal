import logging
import os

from sqlalchemy.exc import SQLAlchemyError

from backend.extensions import db
from backend.models import ComplaintCategory, SystemSetting, User, Ward


logger = logging.getLogger(__name__)

DEFAULT_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@localportal.com")
DEFAULT_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "Admin@123")

DEFAULT_OFFICER_EMAIL = os.getenv("SEED_OFFICER_EMAIL", "officer@localportal.com")
DEFAULT_OFFICER_PASSWORD = os.getenv("SEED_OFFICER_PASSWORD", "Officer@123")

DEFAULT_SECURITY_QUESTION = os.getenv("SEED_SECURITY_QUESTION", "What is your default seed account code?")
DEFAULT_SECURITY_ANSWER = os.getenv("SEED_SECURITY_ANSWER", "LocalPortal")

COMPLAINT_CATEGORIES = (
    "Road Damage",
    "Garbage",
    "Drainage",
    "Water Leakage",
    "Streetlight",
    "Electricity",
    "Public Safety",
    "Others",
)

SYSTEM_SETTINGS = (
    (
        "urgent_escalation_days",
        "7",
        SystemSetting.TYPE_INTEGER,
        "Number of days after which unresolved complaints become urgent.",
    ),
    (
        "critical_escalation_days",
        "15",
        SystemSetting.TYPE_INTEGER,
        "Number of days after which unresolved complaints become critical.",
    ),
    (
        "max_upload_size_mb",
        "5",
        SystemSetting.TYPE_INTEGER,
        "Maximum allowed upload size in megabytes.",
    ),
)


def get_or_create_user(email, full_name, password, role, phone):
    user = User.query.filter(User.email == email).first()
    if user:
        return user, False

    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        role=role,
        security_question=DEFAULT_SECURITY_QUESTION,
        is_active=True,
    )
    user.set_password(password)
    user.set_security_answer(DEFAULT_SECURITY_ANSWER)
    db.session.add(user)
    return user, True


def get_or_create_ward(assigned_officer):
    ward = Ward.query.filter(Ward.ward_code == "W001").first()
    if ward:
        if not ward.assigned_officer_id and assigned_officer:
            ward.assigned_officer = assigned_officer
        return ward, False

    ward = Ward(
        ward_name="Ward 1",
        ward_code="W001",
        assigned_officer=assigned_officer,
        is_active=True,
    )
    db.session.add(ward)
    return ward, True


def seed_complaint_categories():
    created_count = 0

    for category_name in COMPLAINT_CATEGORIES:
        category = ComplaintCategory.query.filter(
            ComplaintCategory.category_name == category_name
        ).first()
        if category:
            continue

        db.session.add(
            ComplaintCategory(
                category_name=category_name,
                description=f"{category_name} related complaints.",
                is_active=True,
            )
        )
        created_count += 1

    return created_count


def seed_system_settings():
    created_count = 0

    for setting_key, setting_value, setting_type, description in SYSTEM_SETTINGS:
        setting = SystemSetting.query.filter(
            SystemSetting.setting_key == setting_key
        ).first()
        if setting:
            continue

        db.session.add(
            SystemSetting(
                setting_key=setting_key,
                setting_value=setting_value,
                setting_type=setting_type,
                description=description,
                is_active=True,
            )
        )
        created_count += 1

    return created_count


def seed_development_data():
    try:
        admin, admin_created = get_or_create_user(
            email=DEFAULT_ADMIN_EMAIL,
            full_name="Default Admin",
            password=DEFAULT_ADMIN_PASSWORD,
            role=User.ROLE_ADMIN,
            phone="9999999999",
        )
        officer, officer_created = get_or_create_user(
            email=DEFAULT_OFFICER_EMAIL,
            full_name="Default Officer",
            password=DEFAULT_OFFICER_PASSWORD,
            role=User.ROLE_OFFICER,
            phone="8888888888",
        )

        db.session.flush()

        ward, ward_created = get_or_create_ward(officer)
        categories_created = seed_complaint_categories()
        settings_created = seed_system_settings()

        db.session.commit()

        logger.info(
            "Seed completed successfully. "
            "Admin=%s Officer=%s Ward=%s WardCreated=%s CategoriesCreated=%s SettingsCreated=%s",
            DEFAULT_ADMIN_EMAIL,
            DEFAULT_OFFICER_EMAIL,
            "W001",
            ward_created,
            categories_created,
            settings_created,
        )

        return {
            "success": True,
            "admin_exists": bool(admin),
            "officer_exists": bool(officer),
            "ward_exists": bool(ward),
            "admin_created": admin_created,
            "officer_created": officer_created,
            "ward_created": ward_created,
            "categories_created": categories_created,
            "settings_created": settings_created,
        }
    except SQLAlchemyError as exc:
        db.session.rollback()
        logger.exception("Seed execution failed. Database changes were rolled back.")
        return {
            "success": False,
            "error": str(exc),
        }
