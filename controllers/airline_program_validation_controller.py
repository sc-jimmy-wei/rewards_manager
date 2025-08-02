from datetime import datetime


class AirlineProgramValidationController:
    """Controller for validating airline program form data."""

    @staticmethod
    def validate_program_form(form_data):
        """Validate airline program form data."""
        errors = []

        # Validate airline name
        airline_name = form_data.get("airline_name", "").strip()
        if not airline_name:
            errors.append("Airline name is required.")
        elif len(airline_name) > 100:
            errors.append("Airline name must be 100 characters or less.")

        # Validate program name
        program_name = form_data.get("program_name", "").strip()
        if not program_name:
            errors.append("Program name is required.")
        elif len(program_name) > 100:
            errors.append("Program name must be 100 characters or less.")

        # Validate account ID
        account_id = form_data.get("account_id", "").strip()
        if not account_id:
            errors.append("Account ID is required.")
        elif len(account_id) > 50:
            errors.append("Account ID must be 50 characters or less.")

        # Validate points
        points = form_data.get("points", "")
        if points and points.strip():
            try:
                points_value = int(points)
                if points_value < 0:
                    errors.append("Points cannot be negative.")
                elif points_value > 10000000:  # 10 million max
                    errors.append("Points cannot exceed 10,000,000.")
            except ValueError:
                errors.append("Points must be a valid number.")

        # Validate expiration date
        expiration_date = form_data.get("expiration_date", "").strip()
        if expiration_date:
            try:
                datetime.strptime(expiration_date, "%Y-%m-%d").date()
                # Check if date is not in the past (optional validation)
                # Commented out to allow past dates for data entry flexibility
                # today = datetime.now().date()
                # if parsed_date < today:
                #     errors.append('Expiration date cannot be in the past.')
            except ValueError:
                errors.append("Expiration date must be in YYYY-MM-DD format.")

        # Validate extension rule (optional field)
        extension_rule = form_data.get("extension_rule", "").strip()
        if extension_rule and len(extension_rule) > 1000:
            errors.append("Extension rule must be 1000 characters or less.")

        return errors
