from datetime import date

from models import AirlineProgram, User, db


class TestAirlineProgramModel:
    """Test cases for AirlineProgram model."""

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

    def test_create_airline_program(self, app_context):
        """Test creating a basic airline program."""
        # Create test user
        user = self.create_test_user()

        program = AirlineProgram(
            airline_name="Delta Air Lines",
            program_name="SkyMiles",
            account_id="SM123456789",
            user_id=user.id,
        )
        db.session.add(program)
        db.session.commit()

        assert program.id is not None
        assert program.airline_name == "Delta Air Lines"
        assert program.program_name == "SkyMiles"
        assert program.account_id == "SM123456789"
        assert program.points == 0  # Default value
        assert program.expiration_date is None
        assert program.extension_rule is None

    def test_create_program_with_all_fields(self, app_context):
        """Test creating a program with all fields."""
        # Create test user
        user = self.create_test_user()

        expiry_date = date(2025, 12, 31)
        program = AirlineProgram(
            airline_name="American Airlines",
            program_name="AAdvantage",
            account_id="AA987654321",
            user_id=user.id,
            points=50000,
            expiration_date=expiry_date,
            extension_rule="Points expire 18 months from date of earning",
        )
        db.session.add(program)
        db.session.commit()

        assert program.airline_name == "American Airlines"
        assert program.program_name == "AAdvantage"
        assert program.account_id == "AA987654321"
        assert program.points == 50000
        assert program.expiration_date == expiry_date
        assert program.extension_rule == "Points expire 18 months from date of earning"

    def test_program_to_dict(self, app_context):
        """Test converting program to dictionary."""
        # Create test user
        user = self.create_test_user()

        expiry_date = date(2025, 6, 15)
        program = AirlineProgram(
            airline_name="United Airlines",
            program_name="MileagePlus",
            account_id="MP456789123",
            user_id=user.id,
            points=25000,
            expiration_date=expiry_date,
            extension_rule="Miles never expire with activity",
        )
        db.session.add(program)
        db.session.commit()

        program_dict = program.to_dict()

        assert program_dict["airline_name"] == "United Airlines"
        assert program_dict["program_name"] == "MileagePlus"
        assert program_dict["account_id"] == "MP456789123"
        assert program_dict["points"] == 25000
        assert program_dict["expiration_date"] == "2025-06-15"
        assert program_dict["extension_rule"] == "Miles never expire with activity"
        assert "id" in program_dict
        assert "created_at" in program_dict
        assert "updated_at" in program_dict

    def test_program_to_dict_with_none_date(self, app_context):
        """Test converting program to dictionary with None expiration date."""
        # Create test user
        user = self.create_test_user()

        program = AirlineProgram(
            airline_name="Southwest Airlines",
            program_name="Rapid Rewards",
            account_id="RR123456789",
            user_id=user.id,
        )
        db.session.add(program)
        db.session.commit()

        program_dict = program.to_dict()
        assert program_dict["expiration_date"] is None

    def test_program_str_representation(self, app_context):
        """Test string representation of airline program."""
        # Create test user
        user = self.create_test_user()

        program = AirlineProgram(
            airline_name="JetBlue Airways",
            program_name="TrueBlue",
            account_id="TB987654321",
            user_id=user.id,
        )

        repr_str = repr(program)
        assert "JetBlue Airways" in repr_str
        assert "TrueBlue" in repr_str
        assert "AirlineProgram" in repr_str

    def test_program_persistence(self, app_context):
        """Test that program data persists in database."""
        # Create test user
        user = self.create_test_user()

        program = AirlineProgram(
            airline_name="Alaska Airlines",
            program_name="Mileage Plan",
            account_id="AS123456789",
            user_id=user.id,
            points=75000,
        )
        db.session.add(program)
        db.session.commit()
        program_id = program.id

        # Clear session to ensure we're reading from DB
        db.session.expunge_all()

        # Retrieve program from database
        retrieved_program = AirlineProgram.query.get(program_id)
        assert retrieved_program is not None
        assert retrieved_program.airline_name == "Alaska Airlines"
        assert retrieved_program.program_name == "Mileage Plan"
        assert retrieved_program.account_id == "AS123456789"
        assert retrieved_program.points == 75000

    def test_program_update(self, app_context):
        """Test updating program properties."""
        # Create test user
        user = self.create_test_user()

        program = AirlineProgram(
            airline_name="Original Airline",
            program_name="Original Program",
            account_id="ORIG123",
            user_id=user.id,
            points=10000,
        )
        db.session.add(program)
        db.session.commit()

        # Update program
        program.airline_name = "Updated Airline"
        program.program_name = "Updated Program"
        program.account_id = "UPD456"
        program.points = 20000
        program.expiration_date = date(2025, 12, 31)
        program.extension_rule = "Updated rule"
        db.session.commit()

        # Verify updates
        updated_program = AirlineProgram.query.get(program.id)
        assert updated_program.airline_name == "Updated Airline"
        assert updated_program.program_name == "Updated Program"
        assert updated_program.account_id == "UPD456"
        assert updated_program.points == 20000
        assert updated_program.expiration_date == date(2025, 12, 31)
        assert updated_program.extension_rule == "Updated rule"

    def test_program_deletion(self, app_context):
        """Test program deletion."""
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
        db.session.delete(program)
        db.session.commit()

        # Verify program is deleted
        assert AirlineProgram.query.get(program_id) is None

    def test_program_queries(self, app_context):
        """Test program queries and filtering."""
        # Create test user
        user = self.create_test_user()

        # Create multiple programs
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

        # Test query all
        all_programs = AirlineProgram.query.all()
        assert len(all_programs) >= 3

        # Test query by airline
        delta_programs = AirlineProgram.query.filter_by(airline_name="Delta").all()
        assert len(delta_programs) >= 2

        # Test query by program name
        skymiles_programs = AirlineProgram.query.filter_by(
            program_name="SkyMiles"
        ).all()
        assert len(skymiles_programs) >= 1

    def test_program_default_values(self, app_context):
        """Test default values for optional fields."""
        # Create test user
        user = self.create_test_user()

        program = AirlineProgram(
            airline_name="Test Airline",
            program_name="Test Program",
            account_id="TEST123",
            user_id=user.id,
        )

        # Test before saving to database
        assert program.points == 0
        assert program.expiration_date is None
        assert program.extension_rule is None

        db.session.add(program)
        db.session.commit()

        # Test after saving to database
        assert program.points == 0
        assert program.expiration_date is None
        assert program.extension_rule is None

    def test_program_with_none_points(self, app_context):
        """Test program with explicitly None points."""
        # Create test user
        user = self.create_test_user()

        program = AirlineProgram(
            airline_name="Test Airline",
            program_name="Test Program",
            account_id="TEST123",
            user_id=user.id,
            points=None,
        )
        db.session.add(program)
        db.session.commit()

        # Should default to 0
        assert program.points == 0
