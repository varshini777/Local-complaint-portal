import pytest
from pathlib import Path
from backend.utils.file_helpers import allowed_upload, save_before_image
from backend.utils.form_helpers import (
    populate_active_category_choices,
    populate_active_ward_choices,
)
from backend.models import ComplaintCategory, Ward
from backend.extensions import db


def test_allowed_upload_valid_extensions(app):
    with app.app_context():
        assert allowed_upload("test.jpg") is True
        assert allowed_upload("test.jpeg") is True
        assert allowed_upload("test.png") is True
        assert allowed_upload("test.webp") is True


def test_allowed_upload_invalid_extensions(app):
    with app.app_context():
        assert allowed_upload("test.exe") is False
        assert allowed_upload("test.pdf") is False
        assert allowed_upload("test.doc") is False
        assert allowed_upload("test.zip") is False


def test_allowed_upload_no_extension(app):
    with app.app_context():
        assert allowed_upload("test") is False
        assert allowed_upload("") is False


def test_allowed_upload_case_insensitive(app):
    with app.app_context():
        assert allowed_upload("test.JPG") is True
        assert allowed_upload("test.PNG") is True
        assert allowed_upload("test.JpEg") is True


def test_populate_active_category_choices(app):
    with app.app_context():
        active = ComplaintCategory(
            category_name="Active Category",
            description="Test",
            is_active=True,
        )
        inactive = ComplaintCategory(
            category_name="Inactive Category",
            description="Test",
            is_active=False,
        )
        db.session.add_all([active, inactive])
        db.session.commit()

        class MockForm:
            category = None

        form = MockForm()
        populate_active_category_choices(form)

        assert form.category is not None
        choices = form.category.choices
        assert len(choices) == 1
        assert choices[0][1] == "Active Category"


def test_populate_active_ward_choices(app):
    with app.app_context():
        active = Ward(
            ward_name="Active Ward",
            ward_code="A001",
            is_active=True,
        )
        inactive = Ward(
            ward_name="Inactive Ward",
            ward_code="I001",
            is_active=False,
        )
        db.session.add_all([active, inactive])
        db.session.commit()

        class MockForm:
            ward = None

        form = MockForm()
        populate_active_ward_choices(form)

        assert form.ward is not None
        choices = form.ward.choices
        assert len(choices) == 1
        assert choices[0][1] == "A001 - Active Ward"


def test_populate_empty_choices(app):
    with app.app_context():
        class MockForm:
            category = None
            ward = None

        form = MockForm()
        populate_active_category_choices(form)
        populate_active_ward_choices(form)

        assert form.category is not None
        assert form.ward is not None
        assert len(form.category.choices) == 0
        assert len(form.ward.choices) == 0
