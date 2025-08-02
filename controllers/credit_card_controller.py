import random
from datetime import date, datetime, timedelta
from flask_login import current_user
from models.credit_card import db, CreditCard
from models.benefit import BenefitTemplate, BenefitTracker


class CreditCardController:
    """Handles business logic for credit card operations."""

    @staticmethod
    def get_all_cards(user_id=None, admin_view=False):
        """Get all credit cards for a user or admin view."""
        if admin_view and current_user.is_authenticated and current_user.is_admin():
            return CreditCard.query.all()
        elif user_id:
            return CreditCard.query.filter_by(user_id=user_id).all()
        elif current_user.is_authenticated:
            return CreditCard.query.filter_by(user_id=current_user.id).all()
        else:
            return []

    @staticmethod
    def get_card_by_id(card_id, user_id=None):
        """Get a credit card by ID, ensuring user has access."""
        card = CreditCard.query.get(card_id)
        if not card:
            return None

        # Admin can access any card
        if current_user.is_authenticated and current_user.is_admin():
            return card

        # Check if user owns this card
        if current_user.is_authenticated and card.user_id == current_user.id:
            return card

        # If specific user_id provided (for admin functionality)
        if user_id and card.user_id == user_id:
            return card

        # Deny access
        from flask import abort

        abort(403)

    @staticmethod
    def filter_cards(
        bank_filter=None,
        card_type_filter=None,
        search_query=None,
        user_id=None,
        admin_view=False,
    ):
        """Filter credit cards based on criteria."""
        if admin_view and current_user.is_authenticated and current_user.is_admin():
            query = CreditCard.query
        elif user_id:
            query = CreditCard.query.filter_by(user_id=user_id)
        elif current_user.is_authenticated:
            query = CreditCard.query.filter_by(user_id=current_user.id)
        else:
            query = CreditCard.query.filter_by(
                user_id=0
            )  # No results for anonymous users

        # Apply bank filter
        if bank_filter:
            query = query.filter(CreditCard.bank.ilike(f"%{bank_filter}%"))

        # Apply card type filter
        if card_type_filter:
            query = query.filter(CreditCard.card_type == card_type_filter)

        # Apply search filter with regex support
        if search_query:
            # Use LIKE search for better SQLite compatibility
            # For simple patterns, convert regex-like patterns to LIKE
            if search_query.startswith("^"):
                # Handle start-of-string patterns like ^Chase
                like_pattern = f"{search_query[1:]}%"
                query = query.filter(CreditCard.name.ilike(like_pattern))
            elif search_query.endswith("$"):
                # Handle end-of-string patterns
                like_pattern = f"%{search_query[:-1]}"
                query = query.filter(CreditCard.name.ilike(like_pattern))
            else:
                # Default case-insensitive search
                query = query.filter(CreditCard.name.ilike(f"%{search_query}%"))

        return query.all()

    @staticmethod
    def get_filter_options(user_id=None, admin_view=False):
        """Get unique banks and card types for filter dropdowns."""
        if admin_view and current_user.is_authenticated and current_user.is_admin():
            query = db.session.query(CreditCard.bank).distinct()
            all_banks = query.all()
            query = db.session.query(CreditCard.card_type).distinct()
            all_card_types = query.all()
        elif user_id:
            query = (
                db.session.query(CreditCard.bank).filter_by(user_id=user_id).distinct()
            )
            all_banks = query.all()
            query = (
                db.session.query(CreditCard.card_type)
                .filter_by(user_id=user_id)
                .distinct()
            )
            all_card_types = query.all()
        elif current_user.is_authenticated:
            query = (
                db.session.query(CreditCard.bank)
                .filter_by(user_id=current_user.id)
                .distinct()
            )
            all_banks = query.all()
            query = (
                db.session.query(CreditCard.card_type)
                .filter_by(user_id=current_user.id)
                .distinct()
            )
            all_card_types = query.all()
        else:
            all_banks = []
            all_card_types = []

        banks = [bank[0] for bank in all_banks if bank[0]]
        card_types = [card_type[0] for card_type in all_card_types if card_type[0]]

        return banks, card_types

    @staticmethod
    def create_card(form_data, image_filename=None, user_id=None):
        """Create a new credit card from form data."""
        # Determine user_id
        if user_id is None:
            if current_user.is_authenticated:
                user_id = current_user.id
            else:
                raise ValueError("User must be authenticated to create cards")

        # Parse form data
        name = form_data["name"].strip()
        bank = form_data["bank"].strip()
        card_type = form_data["card_type"].strip()
        opening_date = datetime.strptime(form_data["opening_date"], "%Y-%m-%d").date()
        credit_limit = int(form_data["credit_limit"])
        account_type = form_data["account_type"].strip()

        # Process benefits with types
        benefit_names = [b.strip() for b in form_data.getlist("benefits") if b.strip()]
        benefit_types = form_data.getlist("benefit_types")

        # Combine benefits with their types
        benefits = []
        for i, benefit_name in enumerate(benefit_names):
            benefit_type = benefit_types[i] if i < len(benefit_types) else "Credit"
            benefits.append({"name": benefit_name, "type": benefit_type})

        # Create new card
        new_card = CreditCard(
            name=name,
            bank=bank,
            card_type=card_type,
            user_id=user_id,
            image_filename=image_filename,
            opening_date=opening_date,
            credit_limit=credit_limit,
            account_type=account_type,
        )
        new_card.set_benefits_list(benefits)

        db.session.add(new_card)
        db.session.commit()

        return new_card

    @staticmethod
    def update_card(card, form_data, new_image_filename=None):
        """Update an existing credit card with form data."""
        # Update basic fields
        card.name = form_data["name"].strip()
        card.bank = form_data["bank"].strip()
        card.card_type = form_data["card_type"].strip()
        card.opening_date = datetime.strptime(
            form_data["opening_date"], "%Y-%m-%d"
        ).date()
        card.credit_limit = int(form_data["credit_limit"])
        card.account_type = form_data["account_type"].strip()

        # Update benefits with types
        benefit_names = [b.strip() for b in form_data.getlist("benefits") if b.strip()]
        benefit_types = form_data.getlist("benefit_types")

        # Combine benefits with their types
        benefits = []
        for i, benefit_name in enumerate(benefit_names):
            benefit_type = benefit_types[i] if i < len(benefit_types) else "Credit"
            benefits.append({"name": benefit_name, "type": benefit_type})

        card.set_benefits_list(benefits)

        # Update image if provided
        if new_image_filename:
            old_image = card.image_filename
            card.image_filename = new_image_filename
            return old_image  # Return old filename for deletion

        db.session.commit()
        return None

    @staticmethod
    def delete_card(card):
        """Delete a credit card."""
        image_filename = card.image_filename
        db.session.delete(card)
        db.session.commit()
        return image_filename  # Return filename for cleanup

    @staticmethod
    def update_benefits_usage(card, usage_data):
        """Update the benefits usage for a card."""
        card.set_benefits_usage(usage_data)
        db.session.commit()

    @staticmethod
    def generate_test_card(user_id=None):
        """Generate a test credit card with realistic data."""
        # Determine user_id
        if user_id is None:
            if current_user.is_authenticated:
                user_id = current_user.id
            else:
                raise ValueError("User must be authenticated to create test cards")
        # Real bank names and card combinations
        test_cards = [
            {
                "banks": ["Chase", "JPMorgan Chase"],
                "cards": [
                    "Sapphire Preferred",
                    "Sapphire Reserve",
                    "Freedom Unlimited",
                    "Freedom Flex",
                    "Ink Business Preferred",
                ],
                "types": ["Visa", "Mastercard"],
            },
            {
                "banks": ["American Express", "Amex"],
                "cards": [
                    "Platinum",
                    "Gold",
                    "Green",
                    "Blue Cash Preferred",
                    "Business Platinum",
                ],
                "types": ["American Express"],
            },
            {
                "banks": ["Capital One"],
                "cards": ["Venture X", "Venture", "Savor", "Quicksilver", "Spark Cash"],
                "types": ["Visa", "Mastercard"],
            },
            {
                "banks": ["Discover"],
                "cards": ["It Cash Back", "It Miles", "It Student", "It Secured"],
                "types": ["Discover"],
            },
            {
                "banks": ["Citi", "Citibank"],
                "cards": [
                    "Double Cash",
                    "Premier",
                    "Custom Cash",
                    "Rewards+",
                    "AAdvantage",
                ],
                "types": ["Visa", "Mastercard"],
            },
        ]

        # Select random card data
        card_group = random.choice(test_cards)
        bank = random.choice(card_group["banks"])
        card_name = random.choice(card_group["cards"])
        card_type = random.choice(card_group["types"])

        # Generate random data
        account_type = random.choice(["Personal", "Business"])
        credit_limit = random.choice(
            [1000, 2500, 5000, 10000, 15000, 25000, 35000, 50000]
        )

        # Random opening date within last 3 years
        today = date.today()
        days_ago = random.randint(30, 1095)  # 30 days to 3 years
        opening_date = today - timedelta(days=days_ago)

        # Random benefits based on card type with Credit/Reward types
        benefit_pools = {
            "credit_benefits": [
                "Annual fee waiver",
                "No foreign transaction fees",
                "Balance transfer offer",
                "Intro APR offer",
                "Purchase protection",
                "Extended warranty",
            ],
            "reward_benefits": [
                "2% cash back on all purchases",
                "5% cash back on rotating categories",
                "3x points on dining",
                "2x points on travel",
                "1.5x points on all purchases",
                "Airport lounge access",
                "Travel credits",
                "Elite status benefits",
            ],
        }

        # Generate mix of Credit and Reward benefits
        benefits = []

        # Add 2-3 credit benefits
        credit_benefits = random.sample(
            benefit_pools["credit_benefits"], random.randint(2, 3)
        )
        for benefit in credit_benefits:
            benefits.append({"name": benefit, "type": "Credit"})

        # Add 2-3 reward benefits
        reward_benefits = random.sample(
            benefit_pools["reward_benefits"], random.randint(2, 3)
        )
        for benefit in reward_benefits:
            benefits.append({"name": benefit, "type": "Reward"})

        # Limit to 5 total benefits
        benefits = benefits[:5]

        # Create the test card
        test_card = CreditCard(
            name=card_name,
            bank=bank,
            card_type=card_type,
            user_id=user_id,
            opening_date=opening_date,
            credit_limit=credit_limit,
            account_type=account_type,
        )
        test_card.set_benefits_list(benefits)

        db.session.add(test_card)
        db.session.commit()

        return test_card

    @staticmethod
    def quick_add_card(selected_card_data, user_id=None):
        """Quickly add a predefined credit card with benefits from templates."""
        # Determine user_id
        if user_id is None:
            if current_user.is_authenticated:
                user_id = current_user.id
            else:
                raise ValueError("User must be authenticated to create cards")

        # Parse selected card data (format: "Bank,Card Name")
        try:
            bank, card_name = selected_card_data.split(',', 1)
        except ValueError:
            raise ValueError("Invalid card selection format")

        # Get benefit templates for this card
        benefit_templates = BenefitTemplate.query.filter_by(
            bank=bank, card_name=card_name
        ).all()

        if not benefit_templates:
            raise ValueError(f"No benefit templates found for {bank} {card_name}")

        # Create the credit card with basic info
        new_card = CreditCard(
            name=card_name,
            bank=bank,
            card_type="Credit Card",  # Default type, user can edit later
            user_id=user_id,
            opening_date=date.today(),  # Default to today, user can edit later
            credit_limit=1000,  # Default limit, user can edit later
            account_type="Personal",  # Default type, user can edit later
        )

        # Convert benefit templates to simple benefits list for backward compatibility
        benefits = []
        for template in benefit_templates:
            if template.benefit_type == "Credit":
                benefit_name = template.benefit_name
                if template.amount:
                    benefit_name += f" (${int(template.amount)})"
                if template.frequency:
                    benefit_name += f" - {template.frequency}"
                benefits.append({"name": benefit_name, "type": "Credit"})
            else:  # Reward
                benefit_name = template.benefit_name
                if template.rate:
                    benefit_name += f" ({template.rate}x {template.unit})"
                benefits.append({"name": benefit_name, "type": "Reward"})

        new_card.set_benefits_list(benefits)

        db.session.add(new_card)
        db.session.flush()  # Get the card ID

        # Create benefit trackers for credit benefits only
        for template in benefit_templates:
            if template.benefit_type == "Credit" and template.amount:
                tracker = BenefitTracker(
                    credit_card_id=new_card.id,
                    benefit_template_id=template.id,
                    used_amount=0.0
                )
                db.session.add(tracker)

        db.session.commit()
        return new_card
