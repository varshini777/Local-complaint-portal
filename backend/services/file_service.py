from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


def allowed_upload(filename):
    """
    Check if file extension is allowed for upload.
    
    Args:
        filename: The filename to check
    
    Returns:
        bool: True if allowed, False otherwise
    """
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return extension in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def validate_file_size(file_storage):
    """
    Validate file size against maximum allowed size.
    
    Args:
        file_storage: The file storage object
    
    Returns:
        tuple: (is_valid, error_message)
    """
    max_size = current_app.config["MAX_CONTENT_LENGTH"]
    
    if file_storage and hasattr(file_storage, 'content_length'):
        if file_storage.content_length > max_size:
            return False, f"File size exceeds maximum allowed size of {max_size / (1024 * 1024):.0f} MB"
    
    return True, None


def save_before_image(file_storage):
    """
    Save a before image for a complaint.
    
    Args:
        file_storage: The file storage object
    
    Returns:
        str: Relative path to saved file, or None if no file
    
    Raises:
        ValueError: If file type is invalid
    """
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_upload(file_storage.filename):
        raise ValueError("Invalid image type.")

    is_valid, error_msg = validate_file_size(file_storage)
    if not is_valid:
        raise ValueError(error_msg)

    upload_dir = Path(current_app.config["COMPLAINT_BEFORE_UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[-1].lower()
    filename = f"{uuid4().hex}.{extension}"
    destination = upload_dir / filename
    file_storage.save(destination)

    return f"uploads/complaints/before/{filename}"


def save_after_image(file_storage):
    """
    Save an after image for a complaint resolution.
    
    Args:
        file_storage: The file storage object
    
    Returns:
        str: Relative path to saved file, or None if no file
    
    Raises:
        ValueError: If file type is invalid
    """
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_upload(file_storage.filename):
        raise ValueError("Invalid image type.")

    is_valid, error_msg = validate_file_size(file_storage)
    if not is_valid:
        raise ValueError(error_msg)

    upload_dir = Path(current_app.config["COMPLAINT_AFTER_UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[-1].lower()
    filename = f"{uuid4().hex}.{extension}"
    destination = upload_dir / filename
    file_storage.save(destination)

    return f"uploads/complaints/after/{filename}"


def delete_file(file_path):
    """
    Delete a file from the uploads directory.
    
    Args:
        file_path: Relative path to the file
    
    Returns:
        bool: True if deleted, False otherwise
    """
    if not file_path:
        return False
    
    try:
        full_path = Path(current_app.config["UPLOAD_FOLDER"]) / file_path
        if full_path.exists():
            full_path.unlink()
            return True
    except Exception:
        pass
    
    return False


def get_file_url(file_path):
    """
    Get the URL for a file.
    
    Args:
        file_path: Relative path to the file
    
    Returns:
        str: URL to access the file
    """
    if not file_path:
        return None
    
    return f"/static/{file_path}"
