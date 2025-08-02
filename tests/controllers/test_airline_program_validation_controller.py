
from controllers.airline_program_validation_controller import (
    AirlineProgramValidationController,
)


class TestAirlineProgramValidationController:
    """Test cases for airline program validation controller."""

    def test_validate_program_form_valid_data(self):
        """Test validation with valid data."""
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "SkyMiles",
            "account_id": "SM123456789",
            "points": "50000",
            "expiration_date": "2025-12-31",
            "extension_rule": "Points expire 24 months from date of activity",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert errors == []

    def test_validate_program_form_missing_airline_name(self):
        """Test validation with missing airline name."""
        form_data = {
            "airline_name": "",
            "program_name": "SkyMiles",
            "account_id": "SM123456789",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert "Airline name is required." in errors

    def test_validate_program_form_missing_program_name(self):
        """Test validation with missing program name."""
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "",
            "account_id": "SM123456789",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert "Program name is required." in errors

    def test_validate_program_form_missing_account_id(self):
        """Test validation with missing account ID."""
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "SkyMiles",
            "account_id": "",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert "Account ID is required." in errors

    def test_validate_program_form_airline_name_too_long(self):
        """Test validation with airline name too long."""
        form_data = {
            "airline_name": "A" * 101,  # 101 characters
            "program_name": "SkyMiles",
            "account_id": "SM123456789",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert "Airline name must be 100 characters or less." in errors

    def test_validate_program_form_program_name_too_long(self):
        """Test validation with program name too long."""
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "P" * 101,  # 101 characters
            "account_id": "SM123456789",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert "Program name must be 100 characters or less." in errors

    def test_validate_program_form_account_id_too_long(self):
        """Test validation with account ID too long."""
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "SkyMiles",
            "account_id": "A" * 51,  # 51 characters
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert "Account ID must be 50 characters or less." in errors

    def test_validate_program_form_invalid_points_non_numeric(self):
        """Test validation with non-numeric points."""
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "SkyMiles",
            "account_id": "SM123456789",
            "points": "invalid",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert "Points must be a valid number." in errors

    def test_validate_program_form_negative_points(self):
        """Test validation with negative points."""
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "SkyMiles",
            "account_id": "SM123456789",
            "points": "-1000",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert "Points cannot be negative." in errors

    def test_validate_program_form_points_too_high(self):
        """Test validation with points too high."""
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "SkyMiles",
            "account_id": "SM123456789",
            "points": "10000001",  # Over 10 million
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert "Points cannot exceed 10,000,000." in errors

    def test_validate_program_form_invalid_date_format(self):
        """Test validation with invalid date format."""
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "SkyMiles",
            "account_id": "SM123456789",
            "expiration_date": "invalid-date",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert "Expiration date must be in YYYY-MM-DD format." in errors

    def test_validate_program_form_extension_rule_too_long(self):
        """Test validation with extension rule too long."""
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "SkyMiles",
            "account_id": "SM123456789",
            "extension_rule": "A" * 1001,  # 1001 characters
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert "Extension rule must be 1000 characters or less." in errors

    def test_validate_program_form_empty_optional_fields(self):
        """Test validation with empty optional fields."""
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "SkyMiles",
            "account_id": "SM123456789",
            "points": "",
            "expiration_date": "",
            "extension_rule": "",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert errors == []  # Should be valid

    def test_validate_program_form_whitespace_trimming(self):
        """Test validation with whitespace in fields."""
        form_data = {
            "airline_name": "  Delta Air Lines  ",
            "program_name": "  SkyMiles  ",
            "account_id": "  SM123456789  ",
            "points": "  50000  ",
            "expiration_date": "  2025-12-31  ",
            "extension_rule": "  Points expire 24 months  ",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert errors == []  # Should be valid after trimming

    def test_validate_program_form_multiple_errors(self):
        """Test validation with multiple errors."""
        form_data = {
            "airline_name": "",  # Missing
            "program_name": "",  # Missing
            "account_id": "",  # Missing
            "points": "invalid",  # Invalid
            "expiration_date": "bad-date",  # Invalid format
            "extension_rule": "A" * 1001,  # Too long
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert len(errors) == 6  # Should have all validation errors
        assert "Airline name is required." in errors
        assert "Program name is required." in errors
        assert "Account ID is required." in errors
        assert "Points must be a valid number." in errors
        assert "Expiration date must be in YYYY-MM-DD format." in errors
        assert "Extension rule must be 1000 characters or less." in errors

    def test_validate_program_form_boundary_values(self):
        """Test validation with boundary values."""
        # Test maximum valid values
        form_data = {
            "airline_name": "A" * 100,  # Exactly 100 characters
            "program_name": "P" * 100,  # Exactly 100 characters
            "account_id": "A" * 50,  # Exactly 50 characters
            "points": "10000000",  # Exactly 10 million
            "extension_rule": "A" * 1000,  # Exactly 1000 characters
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert errors == []  # Should be valid

    def test_validate_program_form_edge_case_points(self):
        """Test validation with edge case points values."""
        # Test zero points
        form_data = {
            "airline_name": "Delta Air Lines",
            "program_name": "SkyMiles",
            "account_id": "SM123456789",
            "points": "0",
        }

        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert errors == []  # Zero should be valid

        # Test maximum valid points
        form_data["points"] = "10000000"
        errors = AirlineProgramValidationController.validate_program_form(form_data)
        assert errors == []  # 10 million should be valid
