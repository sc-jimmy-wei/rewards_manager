import json
from datetime import date

from models import CreditCard, User, db


class TestCreditCardModel:
    """Test cases for CreditCard model."""

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

    def test_create_credit_card(self, app_context):
        """Test creating a basic credit card."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Test Card", bank="Test Bank", card_type="Visa", user_id=user.id
        )
        db.session.add(card)
        db.session.commit()

        assert card.id is not None
        assert card.name == "Test Card"
        assert card.bank == "Test Bank"
        assert card.card_type == "Visa"
        assert card.benefits == "[]"
        assert card.benefits_usage == "{}"

    def test_create_card_with_benefits(self, app_context):
        """Test creating a card with benefits."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Benefits Card",
            bank="Benefits Bank",
            card_type="Mastercard",
            user_id=user.id,
        )
        benefits = [
            {"name": "2x points", "type": "Reward"},
            {"name": "No annual fee", "type": "Credit"},
        ]
        card.set_benefits_list(benefits)

        db.session.add(card)
        db.session.commit()

        assert card.get_benefits_list() == benefits

    def test_create_card_with_image(self, app_context):
        """Test creating a card with image filename."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Image Card",
            bank="Image Bank",
            card_type="American Express",
            user_id=user.id,
            image_filename="test_image.png",
        )
        db.session.add(card)
        db.session.commit()

        assert card.image_filename == "test_image.png"

    def test_get_benefits_list_empty(self, app_context):
        """Test getting empty benefits list."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Empty Benefits",
            bank="Empty Bank",
            card_type="Discover",
            user_id=user.id,
        )

        assert card.get_benefits_list() == []

    def test_get_benefits_list_with_data(self, app_context):
        """Test getting benefits list with new dict structure."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Benefits Card",
            bank="Benefits Bank",
            card_type="Visa",
            user_id=user.id,
        )
        benefits = [
            {"name": "Cash back", "type": "Reward"},
            {"name": "Travel insurance", "type": "Credit"},
            {"name": "Extended warranty", "type": "Credit"},
        ]
        card.set_benefits_list(benefits)

        assert card.get_benefits_list() == benefits

    def test_get_benefits_usage_empty(self, app_context):
        """Test getting empty benefits usage."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Usage Card",
            bank="Usage Bank",
            card_type="Mastercard",
            user_id=user.id,
        )

        assert card.get_benefits_usage() == {}

    def test_backward_compatibility_old_benefits(self, app_context):
        """Test backward compatibility with old string-format benefits."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Legacy Card", bank="Legacy Bank", card_type="Visa", user_id=user.id
        )
        # Simulate old data format stored in database
        card.benefits = '["Old benefit 1", "Old benefit 2"]'

        # Should automatically convert to new format with Credit type
        benefits = card.get_benefits_list()
        expected = [
            {"name": "Old benefit 1", "type": "Credit"},
            {"name": "Old benefit 2", "type": "Credit"},
        ]
        assert benefits == expected

    def test_get_credit_benefits(self, app_context):
        """Test getting only Credit type benefits."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Mixed Card", bank="Mixed Bank", card_type="Visa", user_id=user.id
        )
        benefits = [
            {"name": "No annual fee", "type": "Credit"},
            {"name": "Cash back", "type": "Reward"},
            {"name": "Purchase protection", "type": "Credit"},
            {"name": "Travel points", "type": "Reward"},
        ]
        card.set_benefits_list(benefits)

        credit_benefits = card.get_credit_benefits()
        expected_credit = [
            {"name": "No annual fee", "type": "Credit"},
            {"name": "Purchase protection", "type": "Credit"},
        ]
        assert credit_benefits == expected_credit

    def test_get_reward_benefits(self, app_context):
        """Test getting only Reward type benefits."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Mixed Card", bank="Mixed Bank", card_type="Visa", user_id=user.id
        )
        benefits = [
            {"name": "No annual fee", "type": "Credit"},
            {"name": "Cash back", "type": "Reward"},
            {"name": "Purchase protection", "type": "Credit"},
            {"name": "Travel points", "type": "Reward"},
        ]
        card.set_benefits_list(benefits)

        reward_benefits = card.get_reward_benefits()
        expected_reward = [
            {"name": "Cash back", "type": "Reward"},
            {"name": "Travel points", "type": "Reward"},
        ]
        assert reward_benefits == expected_reward

    def test_empty_benefit_lists_by_type(self, app_context):
        """Test getting empty benefit lists when no benefits of specific type exist."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Empty Type Card", bank="Empty Bank", card_type="Visa", user_id=user.id
        )
        # Only Credit benefits
        benefits = [{"name": "Credit only", "type": "Credit"}]
        card.set_benefits_list(benefits)

        assert len(card.get_credit_benefits()) == 1
        assert len(card.get_reward_benefits()) == 0

        # Only Reward benefits
        benefits = [{"name": "Reward only", "type": "Reward"}]
        card.set_benefits_list(benefits)

        assert len(card.get_credit_benefits()) == 0
        assert len(card.get_reward_benefits()) == 1

    def test_benefit_type_validation(self, app_context):
        """Test that benefit types are properly validated."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Validation Card",
            bank="Validation Bank",
            card_type="Visa",
            user_id=user.id,
        )

        # Test with invalid benefit structure (missing type)
        benefits = [{"name": "Missing type"}]
        card.set_benefits_list(benefits)

        # Should handle gracefully - filter will return empty for missing type
        assert len(card.get_credit_benefits()) == 0
        assert len(card.get_reward_benefits()) == 0

    def test_get_benefits_usage_with_data(self, app_context):
        """Test getting benefits usage with data."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Usage Card", bank="Usage Bank", card_type="Visa", user_id=user.id
        )
        usage = {"Cash back": 5, "Travel insurance": 2}
        card.set_benefits_usage(usage)

        assert card.get_benefits_usage() == usage

    def test_set_benefits_list(self, app_context):
        """Test setting benefits list with new dict structure."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Set Benefits", bank="Set Bank", card_type="Discover", user_id=user.id
        )
        benefits = [
            {"name": "Benefit 1", "type": "Credit"},
            {"name": "Benefit 2", "type": "Reward"},
            {"name": "Benefit 3", "type": "Credit"},
        ]
        card.set_benefits_list(benefits)

        # Check that it's stored as JSON string
        assert card.benefits == json.dumps(benefits)
        # Check that getter returns the list
        assert card.get_benefits_list() == benefits

    def test_set_benefits_usage(self, app_context):
        """Test setting benefits usage."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Set Usage",
            bank="Set Bank",
            card_type="American Express",
            user_id=user.id,
        )
        usage = {"benefit1": 10, "benefit2": 5}
        card.set_benefits_usage(usage)

        # Check that it's stored as JSON string
        assert card.benefits_usage == json.dumps(usage)
        # Check that getter returns the dict
        assert card.get_benefits_usage() == usage

    def test_benefits_json_handling_invalid_data(self, app_context):
        """Test benefits handling with invalid JSON data."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Invalid JSON", bank="Invalid Bank", card_type="Visa", user_id=user.id
        )
        # Manually set invalid JSON
        card.benefits = "invalid json"

        # Should return empty list for invalid JSON
        assert card.get_benefits_list() == []

    def test_benefits_usage_json_handling_invalid_data(self, app_context):
        """Test benefits usage handling with invalid JSON data."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Invalid JSON Usage",
            bank="Invalid Bank",
            card_type="Mastercard",
            user_id=user.id,
        )
        # Manually set invalid JSON
        card.benefits_usage = "invalid json"

        # Should return empty dict for invalid JSON
        assert card.get_benefits_usage() == {}

    def test_card_persistence(self, app_context):
        """Test that card data persists in database."""
        # Create and save card
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Persistence Test",
            bank="Persistence Bank",
            card_type="Visa",
            user_id=user.id,
        )
        card.set_benefits_list([{"name": "Persistent benefit", "type": "Credit"}])
        db.session.add(card)
        db.session.commit()
        card_id = card.id

        # Clear session to ensure we're reading from DB
        db.session.expunge_all()

        # Retrieve card from database
        retrieved_card = CreditCard.query.get(card_id)
        assert retrieved_card is not None
        assert retrieved_card.name == "Persistence Test"
        assert retrieved_card.bank == "Persistence Bank"
        assert retrieved_card.get_benefits_list() == [
            {"name": "Persistent benefit", "type": "Credit"}
        ]

    def test_card_relationships_and_queries(self, app_context):
        """Test card queries and relationships."""
        # Create multiple cards
        user = self.create_test_user()
        card1 = CreditCard(
            name="Card 1", bank="Bank A", card_type="Visa", user_id=user.id
        )
        card2 = CreditCard(
            name="Card 2", bank="Bank B", card_type="Mastercard", user_id=user.id
        )
        card3 = CreditCard(
            name="Card 3", bank="Bank A", card_type="American Express", user_id=user.id
        )

        db.session.add_all([card1, card2, card3])
        db.session.commit()

        # Test query all
        all_cards = CreditCard.query.all()
        assert len(all_cards) >= 3

        # Test query by bank
        bank_a_cards = CreditCard.query.filter_by(bank="Bank A").all()
        assert len(bank_a_cards) >= 2

        # Test query by card type
        visa_cards = CreditCard.query.filter_by(card_type="Visa").all()
        assert len(visa_cards) >= 1

    def test_card_deletion(self, app_context):
        """Test card deletion."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Delete Me", bank="Delete Bank", card_type="Discover", user_id=user.id
        )
        db.session.add(card)
        db.session.commit()
        card_id = card.id

        # Verify card exists
        assert CreditCard.query.get(card_id) is not None

        # Delete card
        db.session.delete(card)
        db.session.commit()

        # Verify card is deleted
        assert CreditCard.query.get(card_id) is None

    def test_card_update(self, app_context):
        """Test updating card properties."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Original Name",
            bank="Original Bank",
            card_type="Visa",
            user_id=user.id,
        )
        db.session.add(card)
        db.session.commit()

        # Update card
        card.name = "Updated Name"
        card.bank = "Updated Bank"
        card.card_type = "Mastercard"
        card.set_benefits_list([{"name": "Updated benefit", "type": "Reward"}])
        db.session.commit()

        # Verify updates
        updated_card = CreditCard.query.get(card.id)
        assert updated_card.name == "Updated Name"
        assert updated_card.bank == "Updated Bank"
        assert updated_card.card_type == "Mastercard"
        assert updated_card.get_benefits_list() == [
            {"name": "Updated benefit", "type": "Reward"}
        ]

    def test_create_card_with_new_fields(self, app_context):
        """Test creating a card with all new fields."""
        opening_date = date(2024, 1, 15)
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Full Card",
            bank="Full Bank",
            card_type="Visa",
            opening_date=opening_date,
            credit_limit=10000,
            account_type="Personal",
            user_id=user.id,
        )
        db.session.add(card)
        db.session.commit()

        assert card.opening_date == opening_date
        assert card.credit_limit == 10000
        assert card.account_type == "Personal"

    def test_create_card_without_new_fields(self, app_context):
        """Test creating a card without optional new fields."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Basic Card",
            bank="Basic Bank",
            card_type="Mastercard",
            user_id=user.id,
        )
        db.session.add(card)
        db.session.commit()

        assert card.opening_date is None
        assert card.credit_limit is None
        assert card.account_type is None

    def test_new_fields_persistence(self, app_context):
        """Test that new fields persist in database."""
        opening_date = date(2023, 6, 1)
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Persistence Card",
            bank="Persistence Bank",
            card_type="American Express",
            opening_date=opening_date,
            credit_limit=25000,
            account_type="Business",
            user_id=user.id,
        )
        db.session.add(card)
        db.session.commit()
        card_id = card.id

        # Clear session
        db.session.expunge_all()

        # Retrieve and verify
        retrieved_card = CreditCard.query.get(card_id)
        assert retrieved_card.opening_date == opening_date
        assert retrieved_card.credit_limit == 25000
        assert retrieved_card.account_type == "Business"

    def test_new_fields_update(self, app_context):
        """Test updating new fields."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Update Card",
            bank="Update Bank",
            card_type="Discover",
            user_id=user.id,
            opening_date=date(2023, 1, 1),
            credit_limit=5000,
            account_type="Personal",
        )
        db.session.add(card)
        db.session.commit()

        # Update fields
        new_date = date(2024, 6, 15)
        card.opening_date = new_date
        card.credit_limit = 15000
        card.account_type = "Business"
        db.session.commit()

        # Verify updates
        updated_card = CreditCard.query.get(card.id)
        assert updated_card.opening_date == new_date
        assert updated_card.credit_limit == 15000
        assert updated_card.account_type == "Business"

    def test_new_fields_null_values(self, app_context):
        """Test handling null values for new fields."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Null Fields",
            bank="Null Bank",
            card_type="Visa",
            opening_date=None,
            credit_limit=None,
            account_type=None,
            user_id=user.id,
        )
        db.session.add(card)
        db.session.commit()
        card_id = card.id

        # Clear session and retrieve
        db.session.expunge_all()
        retrieved_card = CreditCard.query.get(card_id)

        assert retrieved_card.opening_date is None
        assert retrieved_card.credit_limit is None
        assert retrieved_card.account_type is None

    def test_credit_limit_types(self, app_context):
        """Test credit limit with different numeric values."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Limit Card",
            bank="Limit Bank",
            card_type="Mastercard",
            credit_limit=1000,
            user_id=user.id,
        )
        db.session.add(card)
        db.session.commit()

        assert card.credit_limit == 1000
        assert isinstance(card.credit_limit, int)

        # Test updating with different value
        card.credit_limit = 50000
        db.session.commit()
        assert card.credit_limit == 50000

    def test_account_type_values(self, app_context):
        """Test account type with different valid values."""
        # Create test user
        user = self.create_test_user()

        # Test Personal account
        personal_card = CreditCard(
            name="Personal Card",
            bank="Personal Bank",
            card_type="Visa",
            account_type="Personal",
            user_id=user.id,
        )
        db.session.add(personal_card)

        # Test Business account
        business_card = CreditCard(
            name="Business Card",
            bank="Business Bank",
            card_type="American Express",
            account_type="Business",
            user_id=user.id,
        )
        db.session.add(business_card)
        db.session.commit()

        assert personal_card.account_type == "Personal"
        assert business_card.account_type == "Business"

    def test_to_dict_method(self, app_context):
        """Test converting model to dictionary."""
        opening_date = date(2024, 1, 15)
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Dict Card",
            bank="Dict Bank",
            card_type="Visa",
            opening_date=opening_date,
            credit_limit=5000,
            account_type="Personal",
            user_id=user.id,
        )
        card.set_benefits_list(
            [
                {"name": "Benefit 1", "type": "Credit"},
                {"name": "Benefit 2", "type": "Reward"},
            ]
        )
        card.set_benefits_usage({"Benefit 1": 3})
        db.session.add(card)
        db.session.commit()

        card_dict = card.to_dict()

        assert card_dict["name"] == "Dict Card"
        assert card_dict["bank"] == "Dict Bank"
        assert card_dict["card_type"] == "Visa"
        assert card_dict["opening_date"] == "2024-01-15"
        assert card_dict["credit_limit"] == 5000
        assert card_dict["account_type"] == "Personal"
        assert card_dict["benefits"] == [
            {"name": "Benefit 1", "type": "Credit"},
            {"name": "Benefit 2", "type": "Reward"},
        ]
        assert card_dict["benefits_usage"] == {"Benefit 1": 3}

    def test_str_representation(self, app_context):
        """Test string representation of CreditCard."""
        # Create test user
        user = self.create_test_user()

        card = CreditCard(
            name="Repr Card", bank="Repr Bank", card_type="Mastercard", user_id=user.id
        )

        repr_str = repr(card)
        assert "Repr Bank" in repr_str
        assert "Repr Card" in repr_str
        assert "CreditCard" in repr_str
