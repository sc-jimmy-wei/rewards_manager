from io import BytesIO
from PIL import Image
from unittest.mock import patch, MagicMock

from controllers import FileController


class TestFileController:
    """Test cases for FileController."""

    def create_test_image(self, width=100, height=100, format="PNG", color="red"):
        """Helper method to create test images."""
        image = Image.new("RGB", (width, height), color=color)
        img_buffer = BytesIO()
        image.save(img_buffer, format=format)
        img_buffer.seek(0)
        return img_buffer

    def test_allowed_file_valid_extensions(self, app_context):
        """Test allowed_file with valid extensions."""
        assert FileController.allowed_file("test.png") 
        assert FileController.allowed_file("test.jpg") 
        assert FileController.allowed_file("test.jpeg")
        assert FileController.allowed_file("test.gif") 
        assert FileController.allowed_file("test.webp") 
        assert FileController.allowed_file("TEST.PNG")  # Case insensitive

    def test_allowed_file_invalid_extensions(self, app_context):
        """Test allowed_file with invalid extensions."""
        assert not FileController.allowed_file("test.txt") 
        assert not FileController.allowed_file("test.pdf") 
        assert not FileController.allowed_file("test.doc") 
        assert not FileController.allowed_file("test.exe")
        assert not FileController.allowed_file("test")  # No extension

    def test_allowed_file_edge_cases(self, app_context):
        """Test allowed_file with edge cases."""
        assert not FileController.allowed_file("")
        assert (
            FileController.allowed_file(".png") 
        )  # Hidden file with valid extension
        assert FileController.allowed_file("file.name.png") # Multiple dots
        assert (
            not FileController.allowed_file("file.png.txt")
        )  # Valid then invalid extension

    @patch("controllers.file_controller.os.makedirs")
    @patch("controllers.file_controller.Image.open")
    def test_save_uploaded_file_valid_image(
        self, mock_image_open, mock_makedirs, app_context
    ):
        """Test saving a valid image file."""
        # Mock PIL Image
        mock_img = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_img

        # Create mock file
        mock_file = MagicMock()
        mock_file.filename = "test.png"
        mock_file.__bool__.return_value = True

        with patch.object(FileController, "allowed_file", return_value=True):
            with patch(
                "controllers.file_controller.secure_filename", return_value="test.png"
            ):
                result = FileController.save_uploaded_file(mock_file)

        assert result is not None
        assert result.endswith("_test.png")
        mock_makedirs.assert_called_once()
        mock_img.thumbnail.assert_called_once_with((800, 600), Image.Resampling.LANCZOS)
        mock_img.save.assert_called_once()

    def test_save_uploaded_file_invalid_extension(self, app_context):
        """Test saving file with invalid extension."""
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        mock_file.__bool__.return_value = True

        result = FileController.save_uploaded_file(mock_file)
        assert result is None

    def test_save_uploaded_file_no_file(self, app_context):
        """Test saving when no file is provided."""
        result = FileController.save_uploaded_file(None)
        assert result is None

    def test_save_uploaded_file_empty_filename(self, app_context):
        """Test saving file with empty filename."""
        mock_file = MagicMock()
        mock_file.filename = ""
        mock_file.__bool__.return_value = True

        result = FileController.save_uploaded_file(mock_file)
        assert result is None

    @patch("controllers.file_controller.os.makedirs")
    def test_save_uploaded_file_creates_directory(self, mock_makedirs, app_context):
        """Test that upload directory is created if it doesn't exist."""
        mock_file = MagicMock()
        mock_file.filename = "test.png"
        mock_file.__bool__.return_value = True

        with patch.object(FileController, "allowed_file", return_value=True):
            with patch("controllers.file_controller.Image.open"):
                with patch(
                    "controllers.file_controller.secure_filename",
                    return_value="test.png",
                ):
                    FileController.save_uploaded_file(mock_file)

        mock_makedirs.assert_called_once()

    @patch("controllers.file_controller.Image.open")
    def test_save_uploaded_file_corrupted_image(self, mock_image_open, app_context):
        """Test handling corrupted image files."""
        # Mock PIL to raise an exception
        mock_image_open.side_effect = Image.UnidentifiedImageError()

        mock_file = MagicMock()
        mock_file.filename = "corrupted.png"
        mock_file.__bool__.return_value = True

        with patch.object(FileController, "allowed_file", return_value=True):
            result = FileController.save_uploaded_file(mock_file)

        assert result is None

    @patch("controllers.file_controller.uuid.uuid4")
    def test_save_uploaded_file_security_filename(self, mock_uuid, app_context):
        """Test that uploaded filenames are properly secured."""
        mock_uuid.return_value = MagicMock()
        mock_uuid.return_value.__str__.return_value = "test-uuid"

        mock_file = MagicMock()
        mock_file.filename = "../../../etc/passwd.png"
        mock_file.__bool__.return_value = True

        with patch.object(FileController, "allowed_file", return_value=True):
            with patch("controllers.file_controller.Image.open"):
                with patch(
                    "controllers.file_controller.secure_filename"
                ) as mock_secure:
                    mock_secure.return_value = "passwd.png"
                    result = FileController.save_uploaded_file(mock_file)

        assert result == "test-uuid_passwd.png"
        mock_secure.assert_called_once_with("../../../etc/passwd.png")

    @patch("controllers.file_controller.os.path.exists")
    @patch("controllers.file_controller.os.remove")
    def test_delete_file_success(self, mock_remove, mock_exists, app_context):
        """Test successful file deletion."""
        mock_exists.return_value = True

        result = FileController.delete_file("test_file.png")

        assert result
        mock_exists.assert_called_once()
        mock_remove.assert_called_once()

    @patch("controllers.file_controller.os.path.exists")
    def test_delete_file_not_exists(self, mock_exists, app_context):
        """Test deleting non-existent file."""
        mock_exists.return_value = False

        result = FileController.delete_file("nonexistent.png")
        assert not result

    def test_delete_file_no_filename(self, app_context):
        """Test deleting with no filename provided."""
        result = FileController.delete_file(None)
        assert not result

        result = FileController.delete_file("")
        assert not result

    @patch("controllers.file_controller.os.path.exists")
    @patch("controllers.file_controller.os.remove")
    def test_delete_file_os_error(self, mock_remove, mock_exists, app_context):
        """Test handling OS error during file deletion."""
        mock_exists.return_value = True
        mock_remove.side_effect = OSError("Permission denied")

        result = FileController.delete_file("error_file.png")
        assert not result

    @patch("controllers.file_controller.os.makedirs")
    @patch("controllers.file_controller.Image.open")
    def test_save_uploaded_file_large_image_resize(
        self, mock_image_open, mock_makedirs, app_context
    ):
        """Test that large images are properly resized."""
        # Mock PIL Image for large image
        mock_img = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_img

        mock_file = MagicMock()
        mock_file.filename = "large_image.jpg"
        mock_file.__bool__.return_value = True

        with patch.object(FileController, "allowed_file", return_value=True):
            with patch(
                "controllers.file_controller.secure_filename",
                return_value="large_image.jpg",
            ):
                result = FileController.save_uploaded_file(mock_file)

        # Verify the function returns the expected filename
        assert result == "large_image.jpg"
        
        # Verify thumbnail was called with max dimensions
        mock_img.thumbnail.assert_called_once_with((800, 600), Image.Resampling.LANCZOS)

        # Verify save was called with optimization
        mock_img.save.assert_called_once()
        call_args = mock_img.save.call_args
        assert "optimize" in call_args[1]
        assert call_args[1]["optimize"]
        assert "quality" in call_args[1]
        assert call_args[1]["quality"] == 85

    def test_file_path_construction(self, app_context):
        """Test that file paths are constructed correctly."""
        with patch("controllers.file_controller.current_app") as mock_app:
            mock_app.config = {"UPLOAD_FOLDER": "/test/uploads"}

            with patch("controllers.file_controller.os.path.join") as mock_join:
                mock_join.return_value = "/test/uploads/test_file.png"

                with patch(
                    "controllers.file_controller.os.path.exists", return_value=True
                ):
                    with patch("controllers.file_controller.os.remove"):
                        FileController.delete_file("test_file.png")

                mock_join.assert_called_with("/test/uploads", "test_file.png")

    @patch("controllers.file_controller.Image.open")
    def test_save_uploaded_file_various_formats(self, mock_image_open, app_context):
        """Test saving files with various supported formats."""
        mock_img = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_img

        formats = ["test.png", "test.jpg", "test.jpeg", "test.gif", "test.webp"]

        for filename in formats:
            mock_file = MagicMock()
            mock_file.filename = filename
            mock_file.__bool__.return_value = True

            with patch.object(FileController, "allowed_file", return_value=True):
                with patch(
                    "controllers.file_controller.secure_filename", return_value=filename
                ):
                    with patch("controllers.file_controller.os.makedirs"):
                        result = FileController.save_uploaded_file(mock_file)

            assert result is not None
            assert result.endswith(f"_{filename}")

    def test_file_controller_integration_with_app_config(self, app_context):
        """Test that FileController properly uses Flask app configuration."""
        with patch("controllers.file_controller.current_app") as mock_app:
            # Test allowed extensions from config
            mock_app.config = {
                "ALLOWED_EXTENSIONS": {"png", "jpg", "custom"},
                "UPLOAD_FOLDER": "/custom/upload/path",
            }

            # Test with custom extension
            assert FileController.allowed_file("test.custom")
            assert not FileController.allowed_file("test.txt")
