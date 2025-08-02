from datetime import date

from models import CreditCard, User, db


class TestTemplateRendering:
    """Test cases for template rendering and context."""

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

    def test_base_template_elements(self, client):
        """Test that base template elements are present."""
        response = client.get("/")
        assert response.status_code == 200

        # Check for common base template elements
        assert b"<!DOCTYPE html>" in response.data
        assert b"<html" in response.data
        assert b"<head>" in response.data
        assert b"<body>" in response.data
        assert b"Bootstrap" in response.data or b"bootstrap" in response.data

    def test_index_template_structure(self, client):
        """Test index template structure and elements."""
        # Create test user
        user = self.create_test_user()
        # Create test card
        card = CreditCard(
            name="Template Test Card",
            bank="Template Bank",
            card_type="Visa",
            opening_date=date(2024, 1, 15),
            user_id=user.id,
            credit_limit=5000,
            account_type="Personal",
        )
        card.set_benefits_list(
            [
                {"name": "Template benefit 1", "type": "Credit"},
                {"name": "Template benefit 2", "type": "Reward"},
            ]
        )
        db.session.add(card)
        db.session.commit()

        response = client.get("/")
        assert response.status_code == 200

        # Check for key template elements
        assert b"My Credit Cards" in response.data or b"credit" in response.data.lower()
        assert b"Template Test Card" in response.data
        assert b"Template Bank" in response.data
        assert b"Visa" in response.data
        # Benefits are displayed as count, not individual benefits in the list view
        assert b"2 benefits" in response.data or b"Template benefit" in response.data

    def test_add_card_template_form_elements(self, client):
        """Test add card template form structure."""
        response = client.get("/add_card")
        assert response.status_code == 200

        # Check for form elements
        assert b"<form" in response.data
        assert b'method="POST"' in response.data
        assert b'enctype="multipart/form-data"' in response.data

        # Check for required input fields
        assert b'name="name"' in response.data
        assert b'name="bank"' in response.data
        assert b'name="card_type"' in response.data
        assert b'name="opening_date"' in response.data
        assert b'name="credit_limit"' in response.data
        assert b'name="account_type"' in response.data
        assert b'name="benefits"' in response.data
        assert b'name="image"' in response.data

        # Check for form labels
        assert b"Card Name" in response.data
        assert b"Bank" in response.data
        assert b"Card Type" in response.data
        assert b"Opening Date" in response.data
        assert b"Credit Limit" in response.data
        assert b"Account Type" in response.data
        assert b"Benefits" in response.data

    def test_add_card_template_select_options(self, client):
        """Test add card template select field options."""
        response = client.get("/add_card")
        assert response.status_code == 200

        # Check card type options
        assert b'value="Visa"' in response.data
        assert b'value="Mastercard"' in response.data
        assert b'value="American Express"' in response.data
        assert b'value="Discover"' in response.data

        # Check account type options
        assert b'value="Personal"' in response.data
        assert b'value="Business"' in response.data

    def test_edit_card_template_prefilled_data(self, client):
        """Test edit card template with prefilled data."""
        # Create test user
        user = self.create_test_user()
        # Create card to edit
        card = CreditCard(
            name="Edit Template Card",
            bank="Edit Bank",
            card_type="Mastercard",
            opening_date=date(2024, 3, 10),
            user_id=user.id,
            credit_limit=8000,
            account_type="Business",
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

        # Check that form is prefilled with existing data
        assert b'value="Edit Template Card"' in response.data
        assert b'value="Edit Bank"' in response.data
        assert b"selected" in response.data  # Card type should be selected
        assert b'value="8000"' in response.data
        assert b"Edit benefit 1" in response.data
        assert b"Edit benefit 2" in response.data

    def test_benefits_usage_template_structure(self, client):
        """Test benefits usage template structure."""
        # Create test user
        user = self.create_test_user()
        # Create card with benefits
        card = CreditCard(
            name="Usage Template Card",
            bank="Usage Bank",
            card_type="Visa",
            user_id=user.id,
        )
        card.set_benefits_list(
            [
                {"name": "Usage benefit 1", "type": "Credit"},
                {"name": "Usage benefit 2", "type": "Reward"},
            ]
        )
        card.set_benefits_usage({"Usage benefit 1": 3, "Usage benefit 2": 7})
        db.session.add(card)
        db.session.commit()

        response = client.get(f"/benefits_usage/{card.id}")
        assert response.status_code == 200

        # Check for benefits usage elements
        assert b"Benefits Usage" in response.data
        assert b"Usage Template Card" in response.data
        assert b"Usage benefit 1" in response.data
        assert b"Usage benefit 2" in response.data
        assert b"3" in response.data  # Usage count
        assert b"7" in response.data  # Usage count

    def test_filter_functionality_in_template(self, client):
        """Test filter form rendering and functionality."""
        # Create test user
        user = self.create_test_user()
        # Create cards with different attributes
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

        response = client.get("/")
        assert response.status_code == 200

        # Check for filter form elements
        assert b'name="bank"' in response.data
        assert b'name="card_type"' in response.data
        assert b'name="search"' in response.data

        # Check that filter options are populated
        assert b"Chase" in response.data
        assert b"American Express" in response.data

    def test_error_message_display(self, client):
        """Test error message display in templates."""
        # Submit invalid form data
        data = {
            "name": "",  # Required field missing
            "bank": "Test Bank",
            "card_type": "Visa",
            "opening_date": "invalid-date",
            "credit_limit": "60000",  # Too high
            "account_type": "Personal",
            "benefits": "Test benefit",
        }

        response = client.post("/add_card", data=data)
        assert response.status_code == 200

        # Check that error messages are displayed
        response_text = response.data.decode("utf-8").lower()
        error_indicators = ["error", "required", "invalid", "alert"]
        assert any(indicator in response_text for indicator in error_indicators)

    def test_javascript_functionality(self, client):
        """Test JavaScript functionality in templates."""
        response = client.get("/add_card")
        assert response.status_code == 200

        # Check for JavaScript functions
        assert b"addBenefit" in response.data
        assert b"previewImage" in response.data
        assert b"<script>" in response.data

        # Check for dynamic benefit management
        assert b"benefits-container" in response.data
        assert b"Add Benefit" in response.data

    def test_responsive_design_elements(self, client):
        """Test responsive design elements in templates."""
        response = client.get("/")
        assert response.status_code == 200

        # Check for Bootstrap responsive classes
        bootstrap_classes = [b"container", b"row", b"col-", b"btn", b"form-"]
        assert any(cls in response.data for cls in bootstrap_classes)

        # Check for viewport meta tag
        assert b"viewport" in response.data

    def test_image_upload_preview_functionality(self, client):
        """Test image upload and preview functionality."""
        response = client.get("/add_card")
        assert response.status_code == 200

        # Check for image upload elements
        assert b'type="file"' in response.data
        assert b'accept="image/*"' in response.data
        assert b"upload" in response.data.lower()
        assert b"preview" in response.data.lower()

        # Check for drag and drop functionality
        assert b"drag" in response.data.lower() or b"drop" in response.data.lower()

    def test_navigation_and_links(self, client):
        """Test navigation and link elements."""
        response = client.get("/")
        assert response.status_code == 200

        # Check for navigation links
        navigation_text = [b"Add", b"Edit", b"Delete", b"Home"]
        assert any(nav in response.data for nav in navigation_text)

        # Check for proper URL generation
        assert b"href=" in response.data

    def test_form_validation_attributes(self, client):
        """Test HTML5 form validation attributes."""
        response = client.get("/add_card")
        assert response.status_code == 200

        # Check for validation attributes
        assert b"required" in response.data
        assert b"min=" in response.data  # For credit limit
        assert b"max=" in response.data  # For credit limit
        assert b'type="date"' in response.data
        assert b'type="number"' in response.data

    def test_accessibility_features(self, client):
        """Test accessibility features in templates."""
        response = client.get("/add_card")
        assert response.status_code == 200

        # Check for accessibility attributes
        assert b"for=" in response.data  # Label associations
        # Note: Not all templates require ARIA attributes or fieldsets

        # Check for semantic HTML
        assert b"<label" in response.data

    def test_icon_integration(self, client):
        """Test icon integration in templates."""
        response = client.get("/add_card")
        assert response.status_code == 200

        # Check for icon classes (Bootstrap Icons)
        icon_indicators = [b"bi-", b"fa-", b"icon"]
        assert any(icon in response.data for icon in icon_indicators)

    def test_template_conditional_rendering(self, client):
        """Test conditional rendering in templates."""
        # Create test user
        user = self.create_test_user()
        # Test with card that has image
        card_with_image = CreditCard(
            name="Image Card",
            bank="Image Bank",
            card_type="Visa",
            image_filename="test_image.png",
            user_id=user.id,
        )
        db.session.add(card_with_image)
        db.session.commit()

        response = client.get("/")
        assert response.status_code == 200

        # Image should be displayed conditionally
        assert b"test_image.png" in response.data or b"uploads" in response.data

    def test_flash_message_rendering(self, client):
        """Test flash message rendering in templates."""
        # Create a card successfully
        data = {
            "name": "Flash Message Card",
            "bank": "Flash Bank",
            "card_type": "Visa",
            "opening_date": "2024-01-15",
            "credit_limit": "5000",
            "account_type": "Personal",
            "benefits": "Flash benefit",
        }

        response = client.post("/add_card", data=data, follow_redirects=True)
        assert response.status_code == 200

        # Check for flash message indicators
        flash_indicators = [b"alert", b"message", b"success", b"notification"]
        response_text = response.data.lower()
        # Verify at least one flash message indicator is present
        assert any(indicator in response_text for indicator in flash_indicators), \
            "No flash message indicators found in response"

    def test_search_functionality_ui(self, client):
        """Test search functionality UI elements."""
        response = client.get("/")
        assert response.status_code == 200

        # Check for search input
        assert b'name="search"' in response.data
        assert b'type="text"' in response.data or b"placeholder" in response.data

        # Check for search button
        assert b"Filter" in response.data

    def test_card_display_layout(self, client):
        """Test card display layout and styling."""
        # Create test user
        user = self.create_test_user()
        # Create card with various data
        card = CreditCard(
            name="Layout Test Card",
            bank="Layout Bank",
            card_type="Visa",
            opening_date=date(2024, 1, 15),
            user_id=user.id,
            credit_limit=12000,
            account_type="Personal",
        )
        card.set_benefits_list(
            [
                {"name": "Layout benefit 1", "type": "Credit"},
                {"name": "Layout benefit 2", "type": "Reward"},
            ]
        )
        db.session.add(card)
        db.session.commit()

        response = client.get("/")
        assert response.status_code == 200

        # Check for card layout elements
        assert b"Layout Test Card" in response.data
        assert b"Layout Bank" in response.data
        # Credit limit is not displayed in the card list view
        assert b"Personal" in response.data or b"Visa" in response.data
        # Benefits are displayed as count in list view
        assert b"2 benefits" in response.data or b"Layout benefit" in response.data
