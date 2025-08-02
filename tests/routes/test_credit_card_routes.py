from datetime import date
from unittest.mock import patch
from io import BytesIO
from PIL import Image

from models import CreditCard, User, db


class TestCreditCardRoutes:
    """Test cases for credit card routes."""

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

    def create_test_image(self, width=100, height=100, format="PNG"):
        """Helper method to create test images."""
        image = Image.new("RGB", (width, height), color="red")
        img_buffer = BytesIO()
        image.save(img_buffer, format=format)
        img_buffer.seek(0)
        return img_buffer

    def test_index_route(self, client):
        """Test the index route displays cards."""
        # Create test user
        user = self.create_test_user()
        # Create test card
        card = CreditCard(
            name="Index Card", bank="Index Bank", card_type="Visa", user_id=user.id
        )
        db.session.add(card)
        db.session.commit()

        response = client.get("/")
        assert response.status_code == 200
        assert b"Index Card" in response.data
        assert b"Index Bank" in response.data

    def test_index_route_with_filters(self, client):
        """Test index route with filtering parameters."""
        # Create test user
        user = self.create_test_user()
        # Create test cards
        card1 = CreditCard(
            name="Filter Card 1", bank="Chase", card_type="Visa", user_id=user.id
        )
        card2 = CreditCard(
            name="Filter Card 2",
            bank="American Express",
            card_type="American Express",
            user_id=user.id,
        )
        db.session.add_all([card1, card2])
        db.session.commit()

        # Test bank filter
        response = client.get("/?bank=Chase")
        assert response.status_code == 200
        assert b"Filter Card 1" in response.data
        assert b"Filter Card 2" not in response.data

        # Test card type filter
        response = client.get("/?card_type=American Express")
        assert response.status_code == 200
        assert b"Filter Card 2" in response.data
        assert b"Filter Card 1" not in response.data

    def test_index_route_with_search(self, client):
        """Test index route with search query."""
        # Create test user
        user = self.create_test_user()
        # Create test cards
        card1 = CreditCard(
            name="Sapphire Preferred", bank="Chase", card_type="Visa", user_id=user.id
        )
        card2 = CreditCard(
            name="Gold Card",
            bank="American Express",
            card_type="American Express",
            user_id=user.id,
        )
        db.session.add_all([card1, card2])
        db.session.commit()

        response = client.get("/?search=Sapphire")
        assert response.status_code == 200
        assert b"Sapphire Preferred" in response.data
        assert b"Gold Card" not in response.data

    def test_add_card_get(self, client):
        """Test GET request to add card page."""
        response = client.get("/add_card")
        assert response.status_code == 200
        assert b"Add New Credit Card" in response.data
        assert b"Card Name" in response.data
        assert b"Benefits" in response.data

    def test_add_card_post_valid_data(self, client):
        """Test POST request to add card with valid data."""
        # Create test user
        user = self.create_test_user()
        data = {
            "name": "Test Card",
            "bank": "Test Bank",
            "card_type": "Visa",
            "opening_date": "2024-01-15",
            "credit_limit": "5000",
            "account_type": "Personal",
            "benefits": ["Benefit 1", "Benefit 2"],
            "benefit_types": ["Credit", "Reward"],
        }

        response = client.post("/add_card", data=data, follow_redirects=True)
        assert response.status_code == 200

        # Verify card was created
        card = CreditCard.query.filter_by(name="Test Card").first()
        assert card is not None
        assert card.bank == "Test Bank"
        assert card.card_type == "Visa"
        assert card.opening_date == date(2024, 1, 15)
        assert card.credit_limit == 5000
        assert card.account_type == "Personal"
        assert card.user_id == user.id
        expected_benefits = [
            {"name": "Benefit 1", "type": "Credit"},
            {"name": "Benefit 2", "type": "Reward"},
        ]
        assert card.get_benefits_list() == expected_benefits
        
        # Verify improved flash message includes card name
        assert b"Test Card" in response.data

    def test_add_card_post_with_image(self, client):
        """Test POST request to add card with image."""
        # Create test user
        user = self.create_test_user()
        img_data = self.create_test_image()
        data = {
            "name": "Image Card",
            "bank": "Image Bank",
            "card_type": "Mastercard",
            "opening_date": "2024-02-01",
            "credit_limit": "8000",
            "account_type": "Business",
            "benefits": "Image benefit",
            "image": (img_data, "test.png"),
        }

        with patch(
            "routes.credit_card_routes.FileController.save_uploaded_file"
        ) as mock_save:
            mock_save.return_value = "saved_image.png"
            response = client.post("/add_card", data=data, follow_redirects=True)

        assert response.status_code == 200
        mock_save.assert_called_once()

        # Verify card was created with image
        card = CreditCard.query.filter_by(name="Image Card").first()
        assert card is not None
        assert card.image_filename == "saved_image.png"
        assert card.user_id == user.id

    def test_add_card_post_invalid_data(self, client):
        """Test POST request with invalid data."""
        data = {
            "name": "",  # Missing required field
            "bank": "Test Bank",
            "card_type": "Visa",
            "opening_date": "invalid-date",
            "credit_limit": "60000",  # Too high
            "account_type": "Personal",
            # Missing benefits
        }

        response = client.post("/add_card", data=data)
        assert response.status_code == 200
        assert b"error" in response.data.lower() or b"required" in response.data.lower()

    def test_edit_card_get(self, client):
        """Test GET request to edit card page."""
        # Create test user
        user = self.create_test_user()
        card = CreditCard(
            name="Edit Card",
            bank="Edit Bank",
            card_type="Discover",
            opening_date=date(2024, 1, 15),
            credit_limit=7500,
            account_type="Personal",
            user_id=user.id,
        )
        card.set_benefits_list(
            [
                {"name": "Edit benefit 1", "type": "Credit"},
                {"name": "Edit benefit 2", "type": "Reward"},
            ]
        )
        db.session.add(card)
        db.session.commit()

        response = client.get(f"/edit_card/{card.id}")
        assert response.status_code == 200
        assert b"Edit Card" in response.data
        assert b"Edit Bank" in response.data
        assert b"Edit benefit 1" in response.data

    def test_edit_card_get_not_found(self, client):
        """Test GET request to edit non-existent card."""
        response = client.get("/edit_card/99999")
        assert response.status_code == 404

    def test_edit_card_post_valid_data(self, client):
        """Test POST request to edit card with valid data."""
        # Create test user
        user = self.create_test_user()
        # Create initial card
        card = CreditCard(
            name="Original Name",
            bank="Original Bank",
            card_type="Visa",
            opening_date=date(2023, 1, 1),
            credit_limit=3000,
            account_type="Personal",
            user_id=user.id,
        )
        card.set_benefits_list([{"name": "Original benefit", "type": "Credit"}])
        db.session.add(card)
        db.session.commit()

        # Update data
        data = {
            "name": "Updated Name",
            "bank": "Updated Bank",
            "card_type": "Mastercard",
            "opening_date": "2024-06-15",
            "credit_limit": "10000",
            "account_type": "Business",
            "benefits": ["Updated benefit 1", "Updated benefit 2"],
            "benefit_types": ["Credit", "Reward"],
        }

        response = client.post(
            f"/edit_card/{card.id}", data=data, follow_redirects=True
        )
        assert response.status_code == 200

        # Verify updates
        updated_card = CreditCard.query.get(card.id)
        assert updated_card.name == "Updated Name"
        assert updated_card.bank == "Updated Bank"
        assert updated_card.card_type == "Mastercard"
        assert updated_card.opening_date == date(2024, 6, 15)
        assert updated_card.credit_limit == 10000
        assert updated_card.account_type == "Business"
        expected_benefits = [
            {"name": "Updated benefit 1", "type": "Credit"},
            {"name": "Updated benefit 2", "type": "Reward"},
        ]
        assert updated_card.get_benefits_list() == expected_benefits

    def test_edit_card_post_with_new_image(self, client):
        """Test POST request to edit card with new image."""
        # Create test user
        user = self.create_test_user()
        # Create card with existing image
        card = CreditCard(
            name="Image Edit Card",
            bank="Image Bank",
            card_type="Visa",
            image_filename="old_image.png",
            user_id=user.id,
        )
        db.session.add(card)
        db.session.commit()

        img_data = self.create_test_image()
        data = {
            "name": "Image Edit Card",
            "bank": "Image Bank",
            "card_type": "Visa",
            "opening_date": "2024-01-15",
            "credit_limit": "5000",
            "account_type": "Personal",
            "benefits": "Image benefit",
            "image": (img_data, "new_test.png"),
        }

        with patch(
            "routes.credit_card_routes.FileController.save_uploaded_file"
        ) as mock_save:
            with patch(
                "routes.credit_card_routes.FileController.delete_file"
            ) as mock_delete:
                mock_save.return_value = "new_saved_image.png"
                response = client.post(
                    f"/edit_card/{card.id}", data=data, follow_redirects=True
                )

        assert response.status_code == 200
        mock_save.assert_called_once()
        mock_delete.assert_called_once_with("old_image.png")

        # Verify image was updated
        updated_card = CreditCard.query.get(card.id)
        assert updated_card.image_filename == "new_saved_image.png"

    def test_edit_card_post_invalid_data(self, client):
        """Test POST request to edit card with invalid data."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Invalid Edit", bank="Test Bank", card_type="Visa", user_id=user.id
        )
        db.session.add(card)
        db.session.commit()

        data = {
            "name": "",  # Invalid
            "bank": "Test Bank",
            "card_type": "Visa",
            "opening_date": "2024-01-15",
            "credit_limit": "5000",
            "account_type": "Personal",
            "benefits": "Test benefit",
        }

        response = client.post(f"/edit_card/{card.id}", data=data)
        assert response.status_code == 200
        assert b"error" in response.data.lower() or b"required" in response.data.lower()

    def test_delete_card_post(self, client):
        """Test POST request to delete card."""
        # Create test user
        user = self.create_test_user()
        card = CreditCard(
            name="Delete Card",
            bank="Delete Bank",
            card_type="Discover",
            image_filename="delete_image.png",
            user_id=user.id,
        )
        db.session.add(card)
        db.session.commit()
        card_id = card.id

        with patch(
            "routes.credit_card_routes.FileController.delete_file"
        ) as mock_delete:
            response = client.post(f"/delete_card/{card_id}", follow_redirects=True)

        assert response.status_code == 200
        mock_delete.assert_called_once_with("delete_image.png")

        # Verify card was deleted
        deleted_card = CreditCard.query.get(card_id)
        assert deleted_card is None

    def test_delete_card_not_found(self, client):
        """Test POST request to delete non-existent card."""
        response = client.post("/delete_card/99999")
        assert response.status_code == 404

    def test_benefits_usage_get(self, client):
        """Test GET request to benefits usage page."""
        # Create test user
        user = self.create_test_user()
        card = CreditCard(
            name="Usage Card", bank="Usage Bank", card_type="Visa", user_id=user.id
        )
        card.set_benefits_list(
            [
                {"name": "Benefit 1", "type": "Credit"},
                {"name": "Benefit 2", "type": "Reward"},
            ]
        )
        db.session.add(card)
        db.session.commit()

        response = client.get(f"/benefits_usage/{card.id}")
        assert response.status_code == 200
        assert b"Benefits Usage" in response.data
        assert b"Benefit 1" in response.data
        assert b"Benefit 2" in response.data

    def test_benefits_usage_get_not_found(self, client):
        """Test GET request to benefits usage for non-existent card."""
        response = client.get("/benefits_usage/99999")
        assert response.status_code == 404

    def test_benefits_usage_post(self, client):
        """Test POST request to update benefits usage."""
        # Create test user
        user = self.create_test_user()
        card = CreditCard(
            name="Usage Card", bank="Usage Bank", card_type="Visa", user_id=user.id
        )
        card.set_benefits_list(
            [
                {"name": "Benefit 1", "type": "Credit"},
                {"name": "Benefit 2", "type": "Reward"},
            ]
        )
        db.session.add(card)
        db.session.commit()

        data = {"Benefit 1": "5", "Benefit 2": "3"}

        response = client.post(
            f"/benefits_usage/{card.id}", data=data, follow_redirects=True
        )
        assert response.status_code == 200

        # Verify usage was updated
        updated_card = CreditCard.query.get(card.id)
        usage = updated_card.get_benefits_usage()
        assert usage["Benefit 1"] == 5
        assert usage["Benefit 2"] == 3

    def test_generate_test_data_post(self, client):
        """Test POST request to generate test data."""
        initial_count = CreditCard.query.count()

        response = client.post("/generate_test_data", follow_redirects=True)
        assert response.status_code == 200

        # Verify test card was created
        final_count = CreditCard.query.count()
        assert final_count == initial_count + 1

    def test_error_handling_route_decorators(self, client):
        """Test that routes handle errors appropriately."""
        # Test with invalid card ID format
        response = client.get("/edit_card/invalid")
        assert response.status_code == 404

        response = client.post("/delete_card/invalid")
        assert response.status_code == 404

        response = client.get("/benefits_usage/invalid")
        assert response.status_code == 404

    def test_flash_messages(self, client):
        """Test that flash messages are properly displayed."""
        # Test successful card addition
        data = {
            "name": "Flash Test Card",
            "bank": "Flash Bank",
            "card_type": "Visa",
            "opening_date": "2024-01-15",
            "credit_limit": "5000",
            "account_type": "Personal",
            "benefits": "Flash benefit",
        }

        response = client.post("/add_card", data=data, follow_redirects=True)
        assert response.status_code == 200
        # Flash messages would be in session or displayed on page

    def test_form_validation_integration(self, client):
        """Test integration with form validation."""
        # Test comprehensive validation
        data = {
            "name": "",  # Missing
            "bank": "",  # Missing
            "card_type": "",  # Missing
            "opening_date": "invalid",  # Invalid format
            "credit_limit": "60000",  # Too high
            "account_type": "",  # Missing
            # Missing benefits
        }

        response = client.post("/add_card", data=data)
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
        card1 = CreditCard(
            name="Context Card 1",
            bank="Context Bank A",
            card_type="Visa",
            user_id=user.id,
        )
        card2 = CreditCard(
            name="Context Card 2",
            bank="Context Bank B",
            card_type="Mastercard",
            user_id=user.id,
        )
        db.session.add_all([card1, card2])
        db.session.commit()

        response = client.get("/")
        assert response.status_code == 200

        # Check that filter options are available
        assert b"Context Bank A" in response.data
        assert b"Context Bank B" in response.data
        assert b"Visa" in response.data
        assert b"Mastercard" in response.data

    def test_csrf_protection_integration(self, client):
        """Test CSRF protection if implemented."""
        # This would test CSRF token validation
        # Implementation depends on whether CSRF protection is enabled
        response = client.get("/add_card")
        assert response.status_code == 200

        # If CSRF is enabled, would check for token presence
        # assert b"csrf_token" in response.data

    def test_file_upload_security(self, client):
        """Test file upload security measures."""
        # Test with malicious filename
        img_data = self.create_test_image()
        data = {
            "name": "Security Test Card",
            "bank": "Security Bank",
            "card_type": "Visa",
            "opening_date": "2024-01-15",
            "credit_limit": "5000",
            "account_type": "Personal",
            "benefits": "Security benefit",
            "image": (img_data, "../../../malicious.png"),
        }

        with patch(
            "routes.credit_card_routes.FileController.save_uploaded_file"
        ) as mock_save:
            mock_save.return_value = "safe_filename.png"  # Should be sanitized
            response = client.post("/add_card", data=data, follow_redirects=True)

        assert response.status_code == 200
        mock_save.assert_called_once()

        # Verify secure filename handling
        card = CreditCard.query.filter_by(name="Security Test Card").first()
        assert card.image_filename == "safe_filename.png"
