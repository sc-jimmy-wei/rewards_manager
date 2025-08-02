from datetime import date, timedelta
from werkzeug.datastructures import MultiDict

from controllers import CreditCardController
from models import CreditCard, User, db


class TestCreditCardController:
    """Test cases for CreditCardController."""

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

    def test_get_all_cards(self, app_context):
        """Test getting all credit cards."""
        # Create test user
        user = self.create_test_user()
        # Create test cards
        card1 = CreditCard(
            name="Card 1", bank="Bank A", card_type="Visa", user_id=user.id
        )
        card2 = CreditCard(
            name="Card 2", bank="Bank B", card_type="Mastercard", user_id=user.id
        )
        db.session.add_all([card1, card2])
        db.session.commit()

        cards = CreditCardController.get_all_cards(user_id=user.id)
        assert len(cards) >= 2
        card_names = [card.name for card in cards]
        assert "Card 1" in card_names
        assert "Card 2" in card_names

    def test_get_card_by_id(self, app_context):
        """Test getting a card by ID."""
        # Create test user
        user = self.create_test_user()
        card = CreditCard(
            name="ID Card", bank="ID Bank", card_type="Discover", user_id=user.id
        )
        db.session.add(card)
        db.session.commit()

        retrieved_card = CreditCardController.get_card_by_id(card.id, user_id=user.id)
        assert retrieved_card.id == card.id
        assert retrieved_card.name == "ID Card"

    def test_get_card_by_id_not_found(self, app_context):
        """Test getting a card by non-existent ID."""
        # Create test user for access control
        user = self.create_test_user()
        card = CreditCardController.get_card_by_id(99999, user_id=user.id)
        assert card is None

    def test_filter_cards_no_filters(self, app_context):
        """Test filtering cards with no filters applied."""
        # Create test user
        user = self.create_test_user()
        # Create test cards
        card1 = CreditCard(
            name="Filter Card 1",
            bank="Filter Bank A",
            card_type="Visa",
            user_id=user.id,
        )
        card2 = CreditCard(
            name="Filter Card 2",
            bank="Filter Bank B",
            card_type="Mastercard",
            user_id=user.id,
        )
        db.session.add_all([card1, card2])
        db.session.commit()

        cards = CreditCardController.filter_cards(user_id=user.id)
        assert len(cards) >= 2

    def test_filter_cards_by_bank(self, app_context):
        """Test filtering cards by bank."""
        # Create test user
        user = self.create_test_user()
        # Create test cards
        card1 = CreditCard(
            name="Bank Filter 1", bank="Chase", card_type="Visa", user_id=user.id
        )
        card2 = CreditCard(
            name="Bank Filter 2",
            bank="American Express",
            card_type="American Express",
            user_id=user.id,
        )
        db.session.add_all([card1, card2])
        db.session.commit()

        # Filter by exact bank name
        chase_cards = CreditCardController.filter_cards(
            bank_filter="Chase", user_id=user.id
        )
        assert len(chase_cards) >= 1
        assert all(card.bank == "Chase" for card in chase_cards)

        # Filter by partial bank name
        amex_cards = CreditCardController.filter_cards(
            bank_filter="American", user_id=user.id
        )
        assert len(amex_cards) >= 1
        assert all("American" in card.bank for card in amex_cards)

    def test_filter_cards_by_card_type(self, app_context):
        """Test filtering cards by card type."""
        # Create test user
        user = self.create_test_user()
        # Create test cards
        card1 = CreditCard(
            name="Type Filter 1", bank="Type Bank", card_type="Visa", user_id=user.id
        )
        card2 = CreditCard(
            name="Type Filter 2",
            bank="Type Bank",
            card_type="Mastercard",
            user_id=user.id,
        )
        db.session.add_all([card1, card2])
        db.session.commit()

        visa_cards = CreditCardController.filter_cards(
            card_type_filter="Visa", user_id=user.id
        )
        assert len(visa_cards) >= 1
        assert all(card.card_type == "Visa" for card in visa_cards)

    def test_filter_cards_by_search_query(self, app_context):
        """Test filtering cards by search query."""
        # Create test user
        user = self.create_test_user()
        # Create test cards
        card1 = CreditCard(
            name="Sapphire Preferred",
            bank="Search Bank",
            card_type="Visa",
            user_id=user.id,
        )
        card2 = CreditCard(
            name="Gold Card",
            bank="Search Bank",
            card_type="American Express",
            user_id=user.id,
        )
        db.session.add_all([card1, card2])
        db.session.commit()

        # Test exact match
        sapphire_cards = CreditCardController.filter_cards(
            search_query="Sapphire", user_id=user.id
        )
        assert len(sapphire_cards) >= 1
        assert all("Sapphire" in card.name for card in sapphire_cards)

        # Test case insensitive
        gold_cards = CreditCardController.filter_cards(
            search_query="gold", user_id=user.id
        )
        assert len(gold_cards) >= 1
        assert all("Gold" in card.name for card in gold_cards)

    def test_filter_cards_regex_patterns(self, app_context):
        """Test filtering with regex-like patterns."""
        # Create test user
        user = self.create_test_user()
        # Create test cards
        card1 = CreditCard(
            name="Chase Freedom", bank="Chase", card_type="Visa", user_id=user.id
        )
        card2 = CreditCard(
            name="Freedom Unlimited", bank="Chase", card_type="Visa", user_id=user.id
        )
        db.session.add_all([card1, card2])
        db.session.commit()

        # Test start pattern
        chase_start_cards = CreditCardController.filter_cards(
            search_query="^Chase", user_id=user.id
        )
        assert len(chase_start_cards) >= 1
        assert all(card.name.startswith("Chase") for card in chase_start_cards)

        # Test end pattern
        freedom_end_cards = CreditCardController.filter_cards(
            search_query="Freedom$", user_id=user.id
        )
        assert len(freedom_end_cards) >= 1
        assert all(card.name.endswith("Freedom") for card in freedom_end_cards)

    def test_filter_cards_combined_filters(self, app_context):
        """Test filtering with multiple filters combined."""
        # Create test user
        user = self.create_test_user()
        # Create test cards
        card1 = CreditCard(
            name="Combined Test Visa",
            bank="Combined Bank",
            card_type="Visa",
            user_id=user.id,
        )
        card2 = CreditCard(
            name="Combined Test Master",
            bank="Combined Bank",
            card_type="Mastercard",
            user_id=user.id,
        )
        card3 = CreditCard(
            name="Other Card", bank="Other Bank", card_type="Visa", user_id=user.id
        )
        db.session.add_all([card1, card2, card3])
        db.session.commit()

        # Combine bank and card type filters
        filtered_cards = CreditCardController.filter_cards(
            bank_filter="Combined", card_type_filter="Visa", user_id=user.id
        )
        assert len(filtered_cards) >= 1
        assert all(
            card.bank == "Combined Bank" and card.card_type == "Visa"
            for card in filtered_cards
        )

    def test_get_filter_options(self, app_context):
        """Test getting filter options for dropdowns."""
        # Create test user
        user = self.create_test_user()
        # Create test cards with various banks and types
        card1 = CreditCard(
            name="Options 1", bank="Options Bank A", card_type="Visa", user_id=user.id
        )
        card2 = CreditCard(
            name="Options 2",
            bank="Options Bank B",
            card_type="Mastercard",
            user_id=user.id,
        )
        card3 = CreditCard(
            name="Options 3",
            bank="Options Bank A",
            card_type="American Express",
            user_id=user.id,
        )
        db.session.add_all([card1, card2, card3])
        db.session.commit()

        banks, card_types = CreditCardController.get_filter_options(user_id=user.id)

        assert "Options Bank A" in banks
        assert "Options Bank B" in banks
        assert "Visa" in card_types
        assert "Mastercard" in card_types
        assert "American Express" in card_types

    def test_create_card(self, app_context):
        """Test creating a new credit card."""
        # Create test user
        user = self.create_test_user()
        form_data = MultiDict(
            [
                ("name", "Create Test Card"),
                ("bank", "Create Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
                ("benefits", "Create benefit 1"),
                ("benefits", "Create benefit 2"),
                ("benefit_types", "Credit"),
                ("benefit_types", "Reward"),
            ]
        )

        card = CreditCardController.create_card(form_data, user_id=user.id)

        assert card.name == "Create Test Card"
        assert card.bank == "Create Bank"
        assert card.card_type == "Visa"
        assert card.opening_date == date(2024, 1, 15)
        assert card.credit_limit == 5000
        assert card.account_type == "Personal"
        expected_benefits = [
            {"name": "Create benefit 1", "type": "Credit"},
            {"name": "Create benefit 2", "type": "Reward"},
        ]
        assert card.get_benefits_list() == expected_benefits
        assert card.id is not None  # Should be saved to database

    def test_create_card_with_image(self, app_context):
        """Test creating a card with image filename."""
        # Create test user
        user = self.create_test_user()
        form_data = MultiDict(
            [
                ("name", "Image Create Card"),
                ("bank", "Image Bank"),
                ("card_type", "Mastercard"),
                ("opening_date", "2024-02-01"),
                ("credit_limit", "8000"),
                ("account_type", "Business"),
                ("benefits", "Image benefit"),
            ]
        )

        card = CreditCardController.create_card(
            form_data, image_filename="test_image.png", user_id=user.id
        )

        assert card.image_filename == "test_image.png"
        assert card.name == "Image Create Card"

    def test_update_card(self, app_context):
        """Test updating an existing credit card."""
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
        form_data = MultiDict(
            [
                ("name", "Updated Name"),
                ("bank", "Updated Bank"),
                ("card_type", "Mastercard"),
                ("opening_date", "2024-06-15"),
                ("credit_limit", "10000"),
                ("account_type", "Business"),
                ("benefits", "Updated benefit 1"),
                ("benefits", "Updated benefit 2"),
                ("benefit_types", "Credit"),
                ("benefit_types", "Reward"),
            ]
        )

        old_image = CreditCardController.update_card(card, form_data)

        assert card.name == "Updated Name"
        assert card.bank == "Updated Bank"
        assert card.card_type == "Mastercard"
        assert card.opening_date == date(2024, 6, 15)
        assert card.credit_limit == 10000
        assert card.account_type == "Business"
        expected_benefits = [
            {"name": "Updated benefit 1", "type": "Credit"},
            {"name": "Updated benefit 2", "type": "Reward"},
        ]
        assert card.get_benefits_list() == expected_benefits
        assert old_image is None  # No new image provided

    def test_update_card_with_new_image(self, app_context):
        """Test updating a card with a new image."""
        # Create test user
        user = self.create_test_user()
        # Create card with existing image
        card = CreditCard(
            name="Image Update Card",
            bank="Image Bank",
            card_type="Visa",
            image_filename="old_image.png",
            user_id=user.id,
        )
        db.session.add(card)
        db.session.commit()

        form_data = MultiDict(
            [
                ("name", "Image Update Card"),
                ("bank", "Image Bank"),
                ("card_type", "Visa"),
                ("opening_date", "2024-01-15"),
                ("credit_limit", "5000"),
                ("account_type", "Personal"),
                ("benefits", "Image benefit"),
            ]
        )

        old_image = CreditCardController.update_card(
            card, form_data, new_image_filename="new_image.png"
        )

        assert card.image_filename == "new_image.png"
        assert old_image == "old_image.png"  # Should return old filename for cleanup

    def test_delete_card(self, app_context):
        """Test deleting a credit card."""
        # Create test user
        user = self.create_test_user()
        card = CreditCard(
            name="Delete Test Card",
            bank="Delete Bank",
            card_type="Discover",
            image_filename="delete_image.png",
            user_id=user.id,
        )
        db.session.add(card)
        db.session.commit()
        card_id = card.id

        image_filename = CreditCardController.delete_card(card)

        assert image_filename == "delete_image.png"
        # Verify card is deleted from database
        deleted_card = CreditCard.query.get(card_id)
        assert deleted_card is None

    def test_update_benefits_usage(self, app_context):
        """Test updating benefits usage for a card."""
        # Create test user
        user = self.create_test_user()
        card = CreditCard(
            name="Usage Card", bank="Usage Bank", card_type="Visa", user_id=user.id
        )
        db.session.add(card)
        db.session.commit()

        usage_data = {"benefit1": 5, "benefit2": 3}
        CreditCardController.update_benefits_usage(card, usage_data)

        assert card.get_benefits_usage() == usage_data

    def test_generate_test_card(self, app_context):
        """Test generating a test credit card."""
        # Create test user
        user = self.create_test_user()
        initial_count = CreditCard.query.count()

        test_card = CreditCardController.generate_test_card(user_id=user.id)

        final_count = CreditCard.query.count()
        assert final_count == initial_count + 1
        assert test_card.id is not None
        assert test_card.name is not None
        assert test_card.bank is not None
        assert test_card.card_type is not None
        assert test_card.opening_date is not None
        assert test_card.credit_limit is not None
        assert test_card.account_type in ["Personal", "Business"]
        assert len(test_card.get_benefits_list()) >= 2

    def test_generate_test_card_realistic_data(self, app_context):
        """Test that generated test cards have realistic data."""
        # Create test user
        user = self.create_test_user()
        test_card = CreditCardController.generate_test_card(user_id=user.id)

        # Test valid banks
        valid_banks = [
            "Chase",
            "JPMorgan Chase",
            "American Express",
            "Amex",
            "Capital One",
            "Discover",
            "Citi",
            "Citibank",
        ]
        assert test_card.bank in valid_banks

        # Test valid card names
        valid_card_names = [
            "Sapphire Preferred",
            "Sapphire Reserve",
            "Freedom Unlimited",
            "Freedom Flex",
            "Ink Business Preferred",
            "Platinum",
            "Gold",
            "Green",
            "Blue Cash Preferred",
            "Business Platinum",
            "Venture X",
            "Venture",
            "Savor",
            "Quicksilver",
            "Spark Cash",
            "It Cash Back",
            "It Miles",
            "It Student",
            "It Secured",
            "Double Cash",
            "Premier",
            "Custom Cash",
            "Rewards+",
            "AAdvantage",
        ]
        assert test_card.name in valid_card_names

        # Test valid credit limits
        valid_limits = [1000, 2500, 5000, 10000, 15000, 25000, 35000, 50000]
        assert test_card.credit_limit in valid_limits

        # Test opening date is within last 3 years
        today = date.today()
        three_years_ago = today - timedelta(days=1095)
        thirty_days_ago = today - timedelta(days=30)
        assert three_years_ago <= test_card.opening_date <= thirty_days_ago

    def test_generate_test_card_bank_card_type_consistency(self, app_context):
        """Test that generated cards have consistent bank and card type combinations."""
        # Create test user
        user = self.create_test_user()
        for _ in range(5):  # Generate multiple cards to test consistency
            test_card = CreditCardController.generate_test_card(user_id=user.id)

            # American Express bank should only have American Express card type
            if test_card.bank in ["American Express", "Amex"]:
                assert test_card.card_type == "American Express"

            # Discover bank should only have Discover card type
            elif test_card.bank == "Discover":
                assert test_card.card_type == "Discover"

            # Other banks should have Visa or Mastercard
            elif test_card.bank in [
                "Chase",
                "JPMorgan Chase",
                "Capital One",
                "Citi",
                "Citibank",
            ]:
                assert test_card.card_type in ["Visa", "Mastercard"]

    def test_generate_test_card_benefits_matching(self, app_context):
        """Test that generated benefits have proper structure and types."""
        # Create test user
        user = self.create_test_user()
        # Generate multiple cards to test different benefit patterns
        for _ in range(3):
            test_card = CreditCardController.generate_test_card(user_id=user.id)
            benefits = test_card.get_benefits_list()

            # All benefits should have name and type
            for benefit in benefits:
                assert isinstance(benefit, dict)
                assert "name" in benefit
                assert "type" in benefit
                assert benefit["type"] in ["Credit", "Reward"]
                assert isinstance(benefit["name"], str)
                assert len(benefit["name"]) > 0

            # Should have both Credit and Reward types
            credit_benefits = test_card.get_credit_benefits()
            reward_benefits = test_card.get_reward_benefits()
            assert len(credit_benefits) > 0
            assert len(reward_benefits) > 0
