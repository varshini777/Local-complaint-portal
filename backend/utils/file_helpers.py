from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


def allowed_upload(filename):
    """Check if file extension is allowed for upload."""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return extension in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def save_before_image(file_storage):
    """Save a before image for a complaint."""
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_upload(file_storage.filename):
        raise ValueError("Invalid image type.")

    upload_dir = Path(current_app.config["COMPLAINT_BEFORE_UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[-1].lower()
    filename = f"{uuid4().hex}.{extension}"
    destination = upload_dir / filename
    file_storage.save(destination)

    return f"uploads/complaints/before/{filename}"


def save_after_image(file_storage):
    """Save an after image for a complaint resolution."""
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_upload(file_storage.filename):
        raise ValueError("Invalid image type.")

    upload_dir = Path(current_app.config["COMPLAINT_AFTER_UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[-1].lower()
    filename = f"{uuid4().hex}.{extension}"
    destination = upload_dir / filename
    file_storage.save(destination)

    return f"uploads/complaints/after/{filename}"
