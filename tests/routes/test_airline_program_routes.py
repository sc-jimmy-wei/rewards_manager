from datetime import date

from models import AirlineProgram, User, db


class TestAirlineProgramRoutes:
    """Test cases for airline program routes."""

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

    def test_index_route(self, client):
        """Test the index route displays programs."""
        # Create test user
        user = self.create_test_user()
        # Create test program
        program = AirlineProgram(
            airline_name="Index Airline",
            program_name="Index Program",
            account_id="IDX123",
            user_id=user.id,
        )
        db.session.add(program)
        db.session.commit()

        response = client.get("/airline_programs")
        assert response.status_code == 200
        assert b"Index Airline" in response.data
        assert b"Index Program" in response.data

    def test_index_route_with_filters(self, client):
        """Test index route with filtering parameters."""
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

        # Test airline filter
        response = client.get("/airline_programs?airline_filter=Delta")
        assert response.status_code == 200
        assert b"Delta" in response.data
        # Check that only Delta programs are shown in the results section (not filter options)
        # We can't easily assert "American" is not in response.data because it appears in filter dropdown
        response_content = response.data.decode("utf-8")
        delta_card_count = response_content.count('class="card h-100"')
        assert delta_card_count == 1  # Only one card should be displayed

        # Test program filter
        response = client.get("/airline_programs?program_filter=SkyMiles")
        assert response.status_code == 200
        assert b"SkyMiles" in response.data

    def test_index_route_with_search(self, client):
        """Test index route with search query."""
        # Create test user
        user = self.create_test_user()
        # Create test programs
        program1 = AirlineProgram(
            airline_name="Delta Air Lines",
            program_name="SkyMiles",
            account_id="DL123",
            user_id=user.id,
        )
        program2 = AirlineProgram(
            airline_name="United Airlines",
            program_name="MileagePlus",
            account_id="UA456",
            user_id=user.id,
        )
        db.session.add_all([program1, program2])
        db.session.commit()

        response = client.get("/airline_programs?search_query=Delta")
        assert response.status_code == 200
        assert b"Delta Air Lines" in response.data
        # Check that only Delta programs are shown in the results
        response_content = response.data.decode("utf-8")
        delta_card_count = response_content.count('class="card h-100"')
        assert delta_card_count == 1  # Only one card should match the search

    def test_add_program_get(self, client):
        """Test GET request to add program page."""
        response = client.get("/airline_programs/add")
        assert response.status_code == 200
        assert b"Add New Airline Mileage Program" in response.data
        assert b"Airline Name" in response.data
        assert b"Mileage Program Name" in response.data
        assert b"Account ID" in response.data

    def test_add_program_post_valid_data(self, client):
        """Test POST request to add program with valid data."""
        data = {
            "airline_name": "Test Airline",
            "program_name": "Test Program",
            "account_id": "TEST123",
            "points": "50000",
            "expiration_date": "2025-12-31",
            "extension_rule": "Test rule",
        }

        response = client.post(
            "/airline_programs/add", data=data, follow_redirects=True
        )
        assert response.status_code == 200

        # Verify program was created
        program = AirlineProgram.query.filter_by(airline_name="Test Airline").first()
        assert program is not None
        assert program.program_name == "Test Program"
        assert program.account_id == "TEST123"
        assert program.points == 50000
        assert program.expiration_date == date(2025, 12, 31)
        assert program.extension_rule == "Test rule"

    def test_add_program_post_invalid_data(self, client):
        """Test POST request with invalid data."""
        data = {
            "airline_name": "",  # Missing required field
            "program_name": "Test Program",
            "account_id": "TEST123",
            "points": "invalid",  # Invalid points
        }

        response = client.post("/airline_programs/add", data=data)
        assert response.status_code == 200
        assert b"error" in response.data.lower() or b"required" in response.data.lower()

    def test_edit_program_get(self, client):
        """Test GET request to edit program page."""
        # Create test user
        user = self.create_test_user()
        program = AirlineProgram(
            airline_name="Edit Airline",
            program_name="Edit Program",
            account_id="EDIT123",
            points=25000,
            expiration_date=date(2025, 6, 15),
            user_id=user.id,
            extension_rule="Edit rule",
        )
        db.session.add(program)
        db.session.commit()

        response = client.get(f"/airline_programs/edit/{program.id}")
        assert response.status_code == 200
        assert b"Edit Airline" in response.data
        assert b"Edit Program" in response.data
        assert b"EDIT123" in response.data

    def test_edit_program_get_not_found(self, client):
        """Test GET request to edit non-existent program."""
        response = client.get("/airline_programs/edit/99999")
        assert response.status_code == 404

    def test_edit_program_post_valid_data(self, client):
        """Test POST request to edit program with valid data."""
        # Create test user
        user = self.create_test_user()
        # Create initial program
        program = AirlineProgram(
            airline_name="Original Airline",
            program_name="Original Program",
            account_id="ORIG123",
            points=10000,
            user_id=user.id,
        )
        db.session.add(program)
        db.session.commit()

        # Update data
        data = {
            "airline_name": "Updated Airline",
            "program_name": "Updated Program",
            "account_id": "UPD456",
            "points": "75000",
            "expiration_date": "2025-12-31",
            "extension_rule": "Updated rule",
        }

        response = client.post(
            f"/airline_programs/edit/{program.id}", data=data, follow_redirects=True
        )
        assert response.status_code == 200

        # Verify updates
        updated_program = AirlineProgram.query.get(program.id)
        assert updated_program.airline_name == "Updated Airline"
        assert updated_program.program_name == "Updated Program"
        assert updated_program.account_id == "UPD456"
        assert updated_program.points == 75000
        assert updated_program.expiration_date == date(2025, 12, 31)
        assert updated_program.extension_rule == "Updated rule"

    def test_edit_program_post_invalid_data(self, client):
        """Test POST request to edit program with invalid data."""
        # Create test user
        user = self.create_test_user()
        program = AirlineProgram(
            airline_name="Invalid Edit",
            program_name="Test",
            account_id="TEST",
            user_id=user.id,
        )
        db.session.add(program)
        db.session.commit()

        data = {
            "airline_name": "",  # Invalid
            "program_name": "Test Program",
            "account_id": "TEST123",
        }

        response = client.post(f"/airline_programs/edit/{program.id}", data=data)
        assert response.status_code == 200
        assert b"error" in response.data.lower() or b"required" in response.data.lower()

    def test_delete_program_post(self, client):
        """Test POST request to delete program."""
        # Create test user
        user = self.create_test_user()
        program = AirlineProgram(
            airline_name="Delete Airline",
            program_name="Delete Program",
            account_id="DEL123",
            user_id=user.id,
        )
        db.session.add(program)
        db.session.commit()
        program_id = program.id

        response = client.post(
            f"/airline_programs/delete/{program_id}", follow_redirects=True
        )
        assert response.status_code == 200

        # Verify program was deleted
        deleted_program = AirlineProgram.query.get(program_id)
        assert deleted_program is None

    def test_delete_program_not_found(self, client):
        """Test POST request to delete non-existent program."""
        response = client.post("/airline_programs/delete/99999")
        assert response.status_code == 404

    def test_generate_test_data_post(self, client):
        """Test POST request to generate test data."""
        initial_count = AirlineProgram.query.count()

        response = client.post(
            "/airline_programs/generate_test_data", follow_redirects=True
        )
        assert response.status_code == 200

        # Verify test program was created
        final_count = AirlineProgram.query.count()
        assert final_count == initial_count + 1

    def test_error_handling_route_decorators(self, client):
        """Test that routes handle errors appropriately."""
        # Test with invalid program ID format
        response = client.get("/airline_programs/edit/invalid")
        assert response.status_code == 404

        response = client.post("/airline_programs/delete/invalid")
        assert response.status_code == 404

    def test_flash_messages(self, client):
        """Test that flash messages are properly displayed."""
        # Test successful program addition
        data = {
            "airline_name": "Flash Test Airline",
            "program_name": "Flash Program",
            "account_id": "FLASH123",
        }

        response = client.post(
            "/airline_programs/add", data=data, follow_redirects=True
        )
        assert response.status_code == 200
        # Flash messages would be in session or displayed on page

    def test_form_validation_integration(self, client):
        """Test integration with form validation."""
        # Test comprehensive validation
        data = {
            "airline_name": "",  # Missing
            "program_name": "",  # Missing
            "account_id": "",  # Missing
            "points": "invalid",  # Invalid
            "expiration_date": "bad-date",  # Invalid format
        }

        response = client.post("/airline_programs/add", data=data)
        assert response.status_code == 200

        # Check that form errors are displayed
        response_text = response.data.decode("utf-8").lower()
        error_indicators = ["error", "required", "invalid", "must"]
        assert any(indicator in response_text for indicator in error_indicators)

    def test_template_context_variables(self, client):
        """Test that templates receive proper context variables."""
        # Create test user
        user = self.create_test_user()
        # Create test data for filters
        program1 = AirlineProgram(
            airline_name="Context Airline A",
            program_name="Program A",
            account_id="CA1",
            user_id=user.id,
        )
        program2 = AirlineProgram(
            airline_name="Context Airline B",
            program_name="Program B",
            account_id="CB1",
            user_id=user.id,
        )
        db.session.add_all([program1, program2])
        db.session.commit()

        response = client.get("/airline_programs")
        assert response.status_code == 200

        # Check that filter options are available
        assert b"Context Airline A" in response.data
        assert b"Context Airline B" in response.data
        assert b"Program A" in response.data
        assert b"Program B" in response.data

    def test_empty_programs_list(self, client):
        """Test display when no programs exist."""
        response = client.get("/airline_programs")
        assert response.status_code == 200
        assert (
            b"No airline programs yet" in response.data
            or b"no programs" in response.data.lower()
        )

    def test_program_list_pagination_like_behavior(self, client):
        """Test program list with multiple programs."""
        # Create test user
        user = self.create_test_user()
        # Create multiple programs
        programs = []
        for i in range(5):
            program = AirlineProgram(
                airline_name=f"Airline {i}",
                program_name=f"Program {i}",
                account_id=f"AC{i}",
                user_id=user.id,
            )
            programs.append(program)

        db.session.add_all(programs)
        db.session.commit()

        response = client.get("/airline_programs")
        assert response.status_code == 200

        # Check that all programs are displayed
        for i in range(5):
            assert f"Airline {i}".encode() in response.data

    def test_form_field_validation_attributes(self, client):
        """Test HTML5 form validation attributes."""
        response = client.get("/airline_programs/add")
        assert response.status_code == 200

        # Check for validation attributes
        assert b"required" in response.data
        assert b"maxlength=" in response.data
        assert b'type="date"' in response.data
        assert b'type="number"' in response.data

    def test_navigation_links_present(self, client):
        """Test that navigation links work properly."""
        response = client.get("/airline_programs")
        assert response.status_code == 200

        # Check for navigation elements
        assert b"Add New Program" in response.data
        assert b"Add Test Data" in response.data
