from models import AirlineProgram, db
from datetime import date, datetime
from flask_login import current_user
import random


class AirlineProgramController:
    """Controller for managing airline program operations."""

    @staticmethod
    def get_all_programs(user_id=None, admin_view=False):
        """Get all airline programs for a user or admin view."""
        if admin_view and current_user.is_authenticated and current_user.is_admin():
            return AirlineProgram.query.all()
        elif user_id:
            return AirlineProgram.query.filter_by(user_id=user_id).all()
        elif current_user.is_authenticated:
            return AirlineProgram.query.filter_by(user_id=current_user.id).all()
        else:
            return []

    @staticmethod
    def get_program_by_id(program_id, user_id=None):
        """Get airline program by ID, ensuring user has access."""
        program = AirlineProgram.query.get(program_id)
        if not program:
            return None

        # Admin can access any program
        if current_user.is_authenticated and current_user.is_admin():
            return program

        # Check if user owns this program
        if current_user.is_authenticated and program.user_id == current_user.id:
            return program

        # If specific user_id provided (for admin functionality)
        if user_id and program.user_id == user_id:
            return program

        # Deny access
        from flask import abort

        abort(403)

    @staticmethod
    def filter_programs(
        search_query=None,
        airline_filter=None,
        program_filter=None,
        user_id=None,
        admin_view=False,
    ):
        """Filter airline programs based on search criteria."""
        if admin_view and current_user.is_authenticated and current_user.is_admin():
            query = AirlineProgram.query
        elif user_id:
            query = AirlineProgram.query.filter_by(user_id=user_id)
        elif current_user.is_authenticated:
            query = AirlineProgram.query.filter_by(user_id=current_user.id)
        else:
            query = AirlineProgram.query.filter_by(
                user_id=0
            )  # No results for anonymous users

        if search_query and search_query.strip():
            search_pattern = f"%{search_query.strip()}%"
            query = query.filter(
                db.or_(
                    AirlineProgram.airline_name.ilike(search_pattern),
                    AirlineProgram.program_name.ilike(search_pattern),
                    AirlineProgram.account_id.ilike(search_pattern),
                )
            )

        if airline_filter and airline_filter.strip():
            query = query.filter(AirlineProgram.airline_name == airline_filter)

        if program_filter and program_filter.strip():
            query = query.filter(AirlineProgram.program_name == program_filter)

        return query.all()

    @staticmethod
    def get_filter_options(user_id=None, admin_view=False):
        """Get unique values for filter dropdowns."""
        if admin_view and current_user.is_authenticated and current_user.is_admin():
            airlines = db.session.query(AirlineProgram.airline_name).distinct().all()
            programs = db.session.query(AirlineProgram.program_name).distinct().all()
        elif user_id:
            airlines = (
                db.session.query(AirlineProgram.airline_name)
                .filter_by(user_id=user_id)
                .distinct()
                .all()
            )
            programs = (
                db.session.query(AirlineProgram.program_name)
                .filter_by(user_id=user_id)
                .distinct()
                .all()
            )
        elif current_user.is_authenticated:
            airlines = (
                db.session.query(AirlineProgram.airline_name)
                .filter_by(user_id=current_user.id)
                .distinct()
                .all()
            )
            programs = (
                db.session.query(AirlineProgram.program_name)
                .filter_by(user_id=current_user.id)
                .distinct()
                .all()
            )
        else:
            airlines = []
            programs = []

        return {
            "airlines": [airline[0] for airline in airlines],
            "programs": [program[0] for program in programs],
        }

    @staticmethod
    def create_program(form_data, user_id=None):
        """Create a new airline program from form data."""
        # Determine user_id
        if user_id is None:
            if current_user.is_authenticated:
                user_id = current_user.id
            else:
                raise ValueError("User must be authenticated to create programs")

        # Parse form data
        airline_name = form_data.get("airline_name", "").strip()
        program_name = form_data.get("program_name", "").strip()
        account_id = form_data.get("account_id", "").strip()
        points = form_data.get("points", 0)
        expiration_date = form_data.get("expiration_date")
        extension_rule = form_data.get("extension_rule", "").strip()

        # Convert points to integer
        try:
            points = int(points) if points else 0
        except ValueError:
            points = 0

        # Parse expiration date
        parsed_expiration_date = None
        if expiration_date:
            try:
                parsed_expiration_date = datetime.strptime(
                    expiration_date, "%Y-%m-%d"
                ).date()
            except ValueError:
                pass

        # Create new program
        program = AirlineProgram(
            airline_name=airline_name,
            program_name=program_name,
            account_id=account_id,
            user_id=user_id,
            points=points,
            expiration_date=parsed_expiration_date,
            extension_rule=extension_rule,
        )

        db.session.add(program)
        db.session.commit()
        return program

    @staticmethod
    def update_program(program_id, form_data):
        """Update an existing airline program."""
        program = AirlineProgram.query.get(program_id)
        if not program:
            return None

        # Update fields
        program.airline_name = form_data.get("airline_name", "").strip()
        program.program_name = form_data.get("program_name", "").strip()
        program.account_id = form_data.get("account_id", "").strip()

        # Update points
        try:
            program.points = (
                int(form_data.get("points", 0)) if form_data.get("points") else 0
            )
        except ValueError:
            program.points = 0

        # Update expiration date
        expiration_date = form_data.get("expiration_date")
        if expiration_date:
            try:
                program.expiration_date = datetime.strptime(
                    expiration_date, "%Y-%m-%d"
                ).date()
            except ValueError:
                program.expiration_date = None
        else:
            program.expiration_date = None

        program.extension_rule = form_data.get("extension_rule", "").strip()

        db.session.commit()
        return program

    @staticmethod
    def delete_program(program_id):
        """Delete an airline program."""
        program = AirlineProgram.query.get(program_id)
        if not program:
            return False

        db.session.delete(program)
        db.session.commit()
        return True

    @staticmethod
    def generate_test_program(user_id=None):
        """Generate a test airline program with realistic data."""
        # Determine user_id
        if user_id is None:
            if current_user.is_authenticated:
                user_id = current_user.id
            else:
                raise ValueError("User must be authenticated to create test programs")
        airlines_data = {
            "Delta Air Lines": {
                "program": "SkyMiles",
                "sample_accounts": ["123456789", "SM987654321", "DL456789123"],
            },
            "American Airlines": {
                "program": "AAdvantage",
                "sample_accounts": ["AA987654321", "12345AA678", "ADV123456789"],
            },
            "United Airlines": {
                "program": "MileagePlus",
                "sample_accounts": ["MP456789123", "UA123456789", "MP987654321"],
            },
            "Southwest Airlines": {
                "program": "Rapid Rewards",
                "sample_accounts": ["RR123456789", "SW987654321", "RR456789123"],
            },
            "JetBlue Airways": {
                "program": "TrueBlue",
                "sample_accounts": ["TB123456789", "JB987654321", "TB456789123"],
            },
            "Alaska Airlines": {
                "program": "Mileage Plan",
                "sample_accounts": ["AS123456789", "MP987654321", "AS456789123"],
            },
        }

        extension_rules = [
            "Points expire 24 months from date of activity",
            "Miles never expire as long as account has activity every 18 months",
            "Points expire 18 months from date of earning",
            "Miles can be extended by making a purchase or flight",
            "Points expire after 12 months of inactivity",
            "Miles expire 36 months from date of earning",
        ]

        # Select random airline
        airline_name = random.choice(list(airlines_data.keys()))
        airline_data = airlines_data[airline_name]

        # Generate test program
        program = AirlineProgram(
            airline_name=airline_name,
            program_name=airline_data["program"],
            account_id=random.choice(airline_data["sample_accounts"]),
            user_id=user_id,
            points=random.randint(1000, 250000),
            expiration_date=date(2025, random.randint(1, 12), random.randint(1, 28)),
            extension_rule=random.choice(extension_rules),
        )

        db.session.add(program)
        db.session.commit()
        return program
