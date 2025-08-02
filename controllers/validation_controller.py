from datetime import datetime


class ValidationController:
    """Handles form validation logic."""

    @staticmethod
    def validate_card_form(form_data):
        """Validate card form data and return errors."""
        errors = []

        # Validate required fields
        if not form_data.get("name", "").strip():
            errors.append("Card name is required.")

        if not form_data.get("bank", "").strip():
            errors.append("Bank name is required.")

        if not form_data.get("card_type", "").strip():
            errors.append("Card type is required.")

        if not form_data.get("opening_date", "").strip():
            errors.append("Opening date is required.")

        if not form_data.get("credit_limit", "").strip():
            errors.append("Credit limit is required.")

        if not form_data.get("account_type", "").strip():
            errors.append("Account type is required.")

        # Validate opening date format
        if form_data.get("opening_date"):
            try:
                datetime.strptime(form_data["opening_date"], "%Y-%m-%d")
            except ValueError:
                errors.append("Opening date must be a valid date.")

        # Validate credit limit
        if form_data.get("credit_limit"):
            try:
                credit_limit = int(form_data["credit_limit"])
                if credit_limit <= 0:
                    errors.append("Credit limit must be greater than 0.")
                elif credit_limit > 50000:
                    errors.append("Credit limit must be under $50,000.")
            except ValueError:
                errors.append("Credit limit must be a valid number.")

        # Validate benefits (at least one required)
        benefits_list = (
            form_data.getlist("benefits")
            if hasattr(form_data, "getlist")
            else form_data.get("benefits", [])
        )
        if isinstance(benefits_list, str):
            benefits_list = [benefits_list]
        elif not isinstance(benefits_list, list):
            benefits_list = []

        benefits = [
            b.strip() for b in benefits_list if isinstance(b, str) and b.strip()
        ]
        if not benefits:
            errors.append("At least one benefit is required.")

        return errors
