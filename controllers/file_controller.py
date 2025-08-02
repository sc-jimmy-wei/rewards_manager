import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app


class FileController:
    """Handles file upload and processing logic."""

    @staticmethod
    def allowed_file(filename):
        """Check if the file extension is allowed."""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower()
            in current_app.config["ALLOWED_EXTENSIONS"]
        )

    @staticmethod
    def save_uploaded_file(file):
        """Save and process uploaded image file."""
        if file and FileController.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(
                current_app.config["UPLOAD_FOLDER"], unique_filename
            )

            # Create upload directory if it doesn't exist
            os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)

            try:
                # Process and save the image
                with Image.open(file) as img:
                    # Resize if too large (thumbnail preserves aspect ratio)
                    img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                    # Save with optimization
                    img.save(filepath, optimize=True, quality=85)
                return unique_filename
            except (Image.UnidentifiedImageError, OSError, ValueError):
                # Handle corrupted or invalid image files
                return None
        return None

    @staticmethod
    def delete_file(filename):
        """Delete a file from the upload directory."""
        if filename:
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    return True
                except OSError:
                    return False
        return False
