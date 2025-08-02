from datetime import date

from controllers.airline_program_controller import AirlineProgramController
from models import AirlineProgram, User, db


class TestAirlineProgramController:
    """Test cases for airline program controller."""

    def create_test_user(self):
        """Helper method to create a test user."""
        # Try to get existing test user first
        user = User.query.filter_by(username="testuser").first()
        if user:
            return user

        # Create new user if not exists
        user = User(username="testuser", email="test@example.com", password="test")
        db.session.add(user)
        db.session.commit()
        return user

    def test_get_all_programs(self, app_context):
        """Test getting all airline programs."""
        # Create test user
        user = self.create_test_user()

        # Create test programs
        program1 = AirlineProgram(
            airline_name="Delta",
            program_name="SkyMiles",
            account_id="DL1",
            user_id=user.id,
        )
        program2 = AirlineProgram(
            airline_name="American",
            program_name="AAdvantage",
            account_id="AA1",
            user_id=user.id,
        )
        db.session.add_all([program1, program2])
        db.session.commit()

        programs = AirlineProgramController.get_all_programs(user_id=user.id)
        assert len(programs) >= 2

        program_names = [p.airline_name for p in programs]
        assert "Delta" in program_names
        assert "American" in program_names

    def test_get_program_by_id(self, app_context):
        """Test getting program by ID."""
        # Create test user
        user = self.create_test_user()

        program = AirlineProgram(
            airline_name="United",
            program_name="MileagePlus",
            account_id="UA1",
            user_id=user.id,
        )
        db.session.add(program)
        db.session.commit()

        retrieved_program = AirlineProgramController.get_program_by_id(
            program.id, user_id=user.id
        )
        assert retrieved_program is not None
        assert retrieved_program.airline_name == "United"
        assert retrieved_program.program_name == "MileagePlus"

    def test_get_program_by_id_not_found(self, app_context):
        """Test getting program by non-existent ID."""
        # Create test user for access control
        user = self.create_test_user()
        program = AirlineProgramController.get_program_by_id(99999, user_id=user.id)
        assert program is None

    def test_filter_programs_no_filters(self, app_context):
        """Test filtering programs with no filters applied."""
        # Create test user
        user = self.create_test_user()

        program1 = AirlineProgram(
            airline_name="Delta",
            program_name="SkyMiles",
            account_id="DL1",
            user_id=user.id,
        )
        program2 = AirlineProgram(
            airline_name="American",
            program_name="AAdvantage",
            account_id="AA1",
            user_id=user.id,
        )
        db.session.add_all([program1, program2])
        db.session.commit()

        programs = AirlineProgramController.filter_programs(user_id=user.id)
        assert len(programs) >= 2

    def test_filter_programs_by_search_query(self, app_context):
        """Test filtering programs by search query."""
        # Create test user
        user = self.create_test_user()
        program1 = AirlineProgram(
            airline_name="Delta Air Lines",
            program_name="SkyMiles",
            account_id="DL123",
            user_id=user.id,
        )
        program2 = AirlineProgram(
            airline_name="American Airlines",
            program_name="AAdvantage",
            account_id="AA456",
            user_id=user.id,
        )
        program3 = AirlineProgram(
            airline_name="United Airlines",
            program_name="MileagePlus",
            account_id="UA789",
            user_id=user.id,
        )
        db.session.add_all([program1, program2, program3])
        db.session.commit()

        # Search by airline name
        programs = AirlineProgramController.filter_programs(
            search_query="Delta", user_id=user.id
        )
        assert len(programs) == 1
        assert programs[0].airline_name == "Delta Air Lines"

        # Search by program name
        programs = AirlineProgramController.filter_programs(
            search_query="SkyMiles", user_id=user.id
        )
        assert len(programs) == 1
        assert programs[0].program_name == "SkyMiles"

        # Search by account ID
        programs = AirlineProgramController.filter_programs(
            search_query="AA456", user_id=user.id
        )
        assert len(programs) == 1
        assert programs[0].account_id == "AA456"

    def test_filter_programs_by_airline(self, app_context):
        """Test filtering programs by airline."""
        # Create test user
        user = self.create_test_user()
        program1 = AirlineProgram(
            airline_name="Delta",
            program_name="SkyMiles",
            account_id="DL1",
            user_id=user.id,
        )
        program2 = AirlineProgram(
            airline_name="Delta",
            program_name="Business",
            account_id="DL2",
            user_id=user.id,
        )
        program3 = AirlineProgram(
            airline_name="American",
            program_name="AAdvantage",
            account_id="AA1",
            user_id=user.id,
        )
        db.session.add_all([program1, program2, program3])
        db.session.commit()

        programs = AirlineProgramController.filter_programs(
            airline_filter="Delta", user_id=user.id
        )
        assert len(programs) == 2
        for program in programs:
            assert program.airline_name == "Delta"

    def test_filter_programs_by_program_name(self, app_context):
        """Test filtering programs by program name."""
        # Create test user
        user = self.create_test_user()
        program1 = AirlineProgram(
            airline_name="Delta",
            program_name="SkyMiles",
            account_id="DL1",
            user_id=user.id,
        )
        program2 = AirlineProgram(
            airline_name="American",
            program_name="SkyMiles",
            account_id="AA1",
            user_id=user.id,
        )
        program3 = AirlineProgram(
            airline_name="United",
            program_name="MileagePlus",
            account_id="UA1",
            user_id=user.id,
        )
        db.session.add_all([program1, program2, program3])
        db.session.commit()

        programs = AirlineProgramController.filter_programs(
            program_filter="SkyMiles", user_id=user.id
        )
        assert len(programs) == 2
        for program in programs:
            assert program.program_name == "SkyMiles"

    def test_filter_programs_combined_filters(self, app_context):
        """Test filtering programs with combined filters."""
        # Create test user
        user = self.create_test_user()
        program1 = AirlineProgram(
            airline_name="Delta",
            program_name="SkyMiles",
            account_id="DL1",
            user_id=user.id,
        )
        program2 = AirlineProgram(
            airline_name="Delta",
            program_name="Business",
            account_id="DL2",
            user_id=user.id,
        )
        program3 = AirlineProgram(
            airline_name="American",
            program_name="SkyMiles",
            account_id="AA1",
            user_id=user.id,
        )
        db.session.add_all([program1, program2, program3])
        db.session.commit()

        programs = AirlineProgramController.filter_programs(
            search_query="Delta",
            airline_filter="Delta",
            program_filter="SkyMiles",
            user_id=user.id,
        )
        assert len(programs) == 1
        assert programs[0].airline_name == "Delta"
        assert programs[0].program_name == "SkyMiles"

    def test_get_filter_options(self, app_context):
        """Test getting filter options."""
        # Create test user
        user = self.create_test_user()
        program1 = AirlineProgram(
            airline_name="Delta",
            program_name="SkyMiles",
            account_id="DL1",
            user_id=user.id,
        )
        program2 = AirlineProgram(
            airline_name="American",
            program_name="AAdvantage",
            account_id="AA1",
            user_id=user.id,
        )
        program3 = AirlineProgram(
            airline_name="Delta",
            program_name="Business",
            account_id="DL2",
            user_id=user.id,
        )
        db.session.add_all([program1, program2, program3])
        db.session.commit()

        options = AirlineProgramController.get_filter_options(user_id=user.id)

        assert "airlines" in options
        assert "programs" in options
        assert "Delta" in options["airlines"]
        assert "American" in options["airlines"]
        assert "SkyMiles" in options["programs"]
        assert "AAdvantage" in options["programs"]
        assert "Business" in options["programs"]

    def test_create_program(self, app_context):
        """Test creating a new program."""
        # Create test user
        user = self.create_test_user()

        form_data = {
            "airline_name": "Southwest Airlines",
            "program_name": "Rapid Rewards",
            "account_id": "SW123456789",
            "points": "50000",
            "expiration_date": "2025-12-31",
            "extension_rule": "Points never expire",
        }

        program = AirlineProgramController.create_program(form_data, user_id=user.id)

        assert program.airline_name == "Southwest Airlines"
        assert program.program_name == "Rapid Rewards"
        assert program.account_id == "SW123456789"
        assert program.points == 50000
        assert program.expiration_date == date(2025, 12, 31)
        assert program.extension_rule == "Points never expire"

        # Verify it's saved in database
        saved_program = AirlineProgram.query.get(program.id)
        assert saved_program is not None

    def test_create_program_with_invalid_points(self, app_context):
        """Test creating program with invalid points."""
        # Create test user
        user = self.create_test_user()

        form_data = {
            "airline_name": "Test Airline",
            "program_name": "Test Program",
            "account_id": "TEST123",
            "points": "invalid",
            "expiration_date": "",
            "extension_rule": "",
        }

        program = AirlineProgramController.create_program(form_data, user_id=user.id)
        assert program.points == 0  # Should default to 0 for invalid points

    def test_create_program_with_invalid_date(self, app_context):
        """Test creating program with invalid date."""
        # Create test user
        user = self.create_test_user()

        form_data = {
            "airline_name": "Test Airline",
            "program_name": "Test Program",
            "account_id": "TEST123",
            "points": "1000",
            "expiration_date": "invalid-date",
            "extension_rule": "",
        }

        program = AirlineProgramController.create_program(form_data, user_id=user.id)
        assert program.expiration_date is None  # Should be None for invalid date

    def test_update_program(self, app_context):
        """Test updating an existing program."""
        # Create test user
        user = self.create_test_user()
        # Create initial program
        program = AirlineProgram(
            airline_name="Original Airline",
            program_name="Original Program",
            account_id="ORIG123",
            user_id=user.id,
            points=10000,
        )
        db.session.add(program)
        db.session.commit()

        # Update data
        form_data = {
            "airline_name": "Updated Airline",
            "program_name": "Updated Program",
            "account_id": "UPD456",
            "points": "25000",
            "expiration_date": "2025-06-15",
            "extension_rule": "Updated rule",
        }

        updated_program = AirlineProgramController.update_program(program.id, form_data)

        assert updated_program.airline_name == "Updated Airline"
        assert updated_program.program_name == "Updated Program"
        assert updated_program.account_id == "UPD456"
        assert updated_program.points == 25000
        assert updated_program.expiration_date == date(2025, 6, 15)
        assert updated_program.extension_rule == "Updated rule"

    def test_update_program_not_found(self, app_context):
        """Test updating non-existent program."""
        form_data = {
            "airline_name": "Test",
            "program_name": "Test",
            "account_id": "TEST",
        }

        result = AirlineProgramController.update_program(99999, form_data)
        assert result is None

    def test_delete_program(self, app_context):
        """Test deleting a program."""
        # Create test user
        user = self.create_test_user()

        program = AirlineProgram(
            airline_name="Delete Me",
            program_name="Delete Program",
            account_id="DEL123",
            user_id=user.id,
        )
        db.session.add(program)
        db.session.commit()
        program_id = program.id

        # Verify program exists
        assert AirlineProgram.query.get(program_id) is not None

        # Delete program
        success = AirlineProgramController.delete_program(program_id)
        assert success is True

        # Verify program is deleted
        assert AirlineProgram.query.get(program_id) is None

    def test_delete_program_not_found(self, app_context):
        """Test deleting non-existent program."""
        success = AirlineProgramController.delete_program(99999)
        assert success is False

    def test_generate_test_program(self, app_context):
        """Test generating test program data."""
        # Create test user
        user = self.create_test_user()

        initial_count = AirlineProgram.query.count()

        program = AirlineProgramController.generate_test_program(user_id=user.id)

        assert program is not None
        assert program.airline_name is not None
        assert program.program_name is not None
        assert program.account_id is not None
        assert program.points > 0
        assert program.expiration_date is not None
        assert program.extension_rule is not None

        # Verify count increased
        final_count = AirlineProgram.query.count()
        assert final_count == initial_count + 1

    def test_generate_test_program_realistic_data(self, app_context):
        """Test that generated test data is realistic."""
        # Create test user
        user = self.create_test_user()

        program = AirlineProgramController.generate_test_program(user_id=user.id)

        # Check that airline name is from known airlines
        known_airlines = [
            "Delta Air Lines",
            "American Airlines",
            "United Airlines",
            "Southwest Airlines",
            "JetBlue Airways",
            "Alaska Airlines",
        ]
        assert program.airline_name in known_airlines

        # Check that points are in reasonable range
        assert 1000 <= program.points <= 250000

        # Check that expiration date is in 2025
        assert program.expiration_date.year == 2025
