from werkzeug.datastructures import MultiDict

from controllers import ValidationController


class TestValidationController:
    """Test cases for ValidationController."""

    def test_validate_card_form_valid_data(self):
        """Test validation with completely valid form data."""
        form_data = MultiDict(
            [
                ("name", "Valid Card Name"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit 1"),
                ("benefits", "Valid benefit 2"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert errors == []

    def test_validate_card_form_missing_name(self):
        """Test validation with missing card name."""
        form_data = MultiDict(
            [
                ("name", ""),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Card name is required." in errors

    def test_validate_card_form_missing_bank(self):
        """Test validation with missing bank name."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", ""),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Bank name is required." in errors

    def test_validate_card_form_missing_card_type(self):
        """Test validation with missing card type."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", ""),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Card type is required." in errors

    def test_validate_card_form_missing_opening_date(self):
        """Test validation with missing opening date."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", ""),
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Opening date is required." in errors

    def test_validate_card_form_missing_credit_limit(self):
        """Test validation with missing credit limit."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", ""),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Credit limit is required." in errors

    def test_validate_card_form_missing_account_type(self):
        """Test validation with missing account type."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "5000"),
                ("account_type", ""),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Account type is required." in errors

    def test_validate_card_form_missing_benefits(self):
        """Test validation with missing benefits."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "At least one benefit is required." in errors

    def test_validate_card_form_empty_benefits(self):
        """Test validation with empty benefits."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
                ("benefits", ""),
                ("benefits", "   "),  # Whitespace only
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "At least one benefit is required." in errors

    def test_validate_card_form_invalid_date_format(self):
        """Test validation with invalid date format."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "invalid-date"),
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Opening date must be a valid date." in errors

    def test_validate_card_form_invalid_date_values(self):
        """Test validation with invalid date values."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-13-45"),  # Invalid month and day
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Opening date must be a valid date." in errors

    def test_validate_card_form_credit_limit_zero(self):
        """Test validation with zero credit limit."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "0"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Credit limit must be greater than 0." in errors

    def test_validate_card_form_credit_limit_negative(self):
        """Test validation with negative credit limit."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "-1000"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Credit limit must be greater than 0." in errors

    def test_validate_card_form_credit_limit_too_high(self):
        """Test validation with credit limit over 50k."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "60000"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Credit limit must be under $50,000." in errors

    def test_validate_card_form_credit_limit_exactly_50k(self):
        """Test validation with credit limit exactly at 50k (should be valid)."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "50000"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        # Should not have credit limit error
        credit_limit_errors = [
            error for error in errors if "credit limit" in error.lower()
        ]
        assert len(credit_limit_errors) == 0

    def test_validate_card_form_credit_limit_non_numeric(self):
        """Test validation with non-numeric credit limit."""
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "not-a-number"),
                ("account_type", "Personal"),
                ("benefits", "Valid benefit"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert "Credit limit must be a valid number." in errors

    def test_validate_card_form_whitespace_trimming(self):
        """Test that validation trims whitespace from fields."""
        form_data = MultiDict(
            [
                ("name", "  Valid Card  "),
                ("bank", "  Valid Bank  "),
                ("card_type", "  Visa  "),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "5000"),
                ("account_type", "  Personal  "),
                ("benefits", "  Valid benefit  "),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert errors == []  # Should be valid after trimming

    def test_validate_card_form_multiple_errors(self):
        """Test validation with multiple errors."""
        form_data = MultiDict(
            [
                ("name", ""),  # Missing name
                ("bank", ""),  # Missing bank
                ("card_type", "Visa"),
                ("opening_date", "invalid-date"),  # Invalid date
                ("credit_limit", "60000"),  # Too high credit limit
                ("account_type", "Personal"),
                # Missing benefits
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert len(errors) >= 4  # Should have multiple errors
        assert "Card name is required." in errors
        assert "Bank name is required." in errors
        assert "Opening date must be a valid date." in errors
        assert "Credit limit must be under $50,000." in errors
        assert "At least one benefit is required." in errors

    def test_validate_card_form_benefits_list_handling(self):
        """Test validation with different benefit list formats."""
        # Test with MultiDict format for multiple benefits
        form_data = MultiDict(
            [
                ("name", "Valid Card"),
                ("bank", "Valid Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
                ("benefits", "Benefit 1"),
                ("benefits", "Benefit 2"),
            ]
        )

        errors = ValidationController.validate_card_form(form_data)
        assert errors == []

    def test_validate_card_form_benefits_string_handling(self):
        """Test validation with single benefit as string."""
        form_data = {
            "name": "Valid Card",
            "bank": "Valid Bank",
            "card_type": "Visa",
            "opening_date": "2024-01-15",
            "credit_limit": "5000",
            "account_type": "Personal",
            "benefits": "Single benefit",
        }

        errors = ValidationController.validate_card_form(form_data)
        assert errors == []

    def test_validate_card_form_edge_case_date_formats(self):
        """Test validation with various date formats."""
        valid_dates = [
            "2024-01-01",
            "2024-12-31",
            "2023-02-28",
            "2024-02-29",
        ]  # Leap year

        for date_str in valid_dates:
            form_data = MultiDict(
                [
                    ("name", "Valid Card"),
                    ("bank", "Valid Bank"),
                    ("card_type", "Visa"),
                    ("opening_date", date_str),
                    ("credit_limit", "5000"),
                    ("account_type", "Personal"),
                    ("benefits", "Valid benefit"),
                ]
            )

            errors = ValidationController.validate_card_form(form_data)
            date_errors = [error for error in errors if "date" in error.lower()]
            assert len(date_errors) == 0, f"Date {date_str} should be valid"

    def test_validate_card_form_credit_limit_boundary_values(self):
        """Test validation with boundary credit limit values."""
        boundary_values = [
            ("1", True),  # Minimum valid
            ("50000", True),  # Maximum valid
            ("0", False),  # Below minimum
            ("50001", False),  # Above maximum
        ]

        for limit_str, should_be_valid in boundary_values:
            form_data = MultiDict(
                [
                    ("name", "Valid Card"),
                    ("bank", "Valid Bank"),
                    ("card_type", "Visa"),
                    ("opening_date", "2024-01-15"),
                    ("credit_limit", limit_str),
                    ("account_type", "Personal"),
                    ("benefits", "Valid benefit"),
                ]
            )

            errors = ValidationController.validate_card_form(form_data)
            credit_limit_errors = [
                error for error in errors if "credit limit" in error.lower()
            ]

            if should_be_valid:
                assert len(credit_limit_errors) == 0, (
                    f"Credit limit {limit_str} should be valid"
                )
            else:
                assert len(credit_limit_errors) > 0, (
                    f"Credit limit {limit_str} should be invalid"
                )
