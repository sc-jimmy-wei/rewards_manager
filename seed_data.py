"""
Comprehensive database seeding script for all application data.
This is the single source of truth for seeding users and credit card benefit templates.
"""

from app import create_app
from models import db, User, BenefitTemplate, CardBenefitTemplate
from credit_card_data import CREDIT_CARD_DATA, get_card_image_url, get_card_benefits


def seed_users():
    """Create default admin and test users if they don't exist."""
    try:
        # Check if admin user exists
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@localhost",
                password="admin123",
                first_name="System",
                last_name="Administrator",
                role="admin",
            )
            db.session.add(admin_user)
            print("Created default admin user (username: admin, password: admin123)")
        else:
            print("Admin user already exists")

        # Check if test user exists
        test_user = User.query.filter_by(username="testuser").first()
        if not test_user:
            test_user = User(
                username="testuser",
                email="testuser@localhost",
                password="test123",
                first_name="Test",
                last_name="User",
                role="user",
            )
            db.session.add(test_user)
            print("Created default test user (username: testuser, password: test123)")
        else:
            print("Test user already exists")

        db.session.commit()
        print("User seeding completed successfully!")
        
    except Exception as e:
        print(f"Failed to create default users: {e}")
        db.session.rollback()


def seed_benefit_templates():
    """Seed the database with benefit templates from the benefits data."""
    try:
        # Clear existing data
        BenefitTemplate.query.delete()
        CardBenefitTemplate.query.delete()
        
        # Seed benefit templates
        for bank, cards in CREDIT_CARD_DATA.items():
            for card_name, card_data in cards.items():
                
                # Create card benefit template entry
                card_template = CardBenefitTemplate(bank=bank, card_name=card_name)
                db.session.add(card_template)
                
                # Get card image URL
                card_image_url = get_card_image_url(bank, card_name)
                
                # Add credit benefits
                for credit in card_data.get('credits', []):
                    benefit = BenefitTemplate(
                        bank=bank,
                        card_name=card_name,
                        benefit_name=credit['name'],
                        benefit_type='Credit',
                        category=credit.get('category'),
                        amount=credit.get('amount'),
                        frequency=credit.get('frequency'),
                        note=credit.get('note'),
                        image_url=card_image_url
                    )
                    db.session.add(benefit)
                
                # Add reward benefits
                for reward in card_data.get('rewards', []):
                    benefit = BenefitTemplate(
                        bank=bank,
                        card_name=card_name,
                        benefit_name=f"{reward['category'].replace('_', ' ').title()} Rewards",
                        benefit_type='Reward',
                        category=reward['category'],
                        rate=reward['rate'],
                        unit=reward['unit'],
                        note=reward.get('note'),
                        image_url=card_image_url
                    )
                    db.session.add(benefit)
        
        db.session.commit()
        print("Benefit templates seeded successfully!")
        
    except Exception as e:
        print(f"Failed to seed benefit templates: {e}")
        db.session.rollback()


def seed_all():
    """Comprehensive database seeding function that creates users and benefit templates."""
    app = create_app()
    
    with app.app_context():
        print("Starting comprehensive database seeding...")
        print("=" * 50)
        
        # Seed users first
        print("1. Seeding users...")
        seed_users()
        print()
        
        # Seed benefit templates
        print("2. Seeding benefit templates...")
        seed_benefit_templates()
        print()
        
        print("=" * 50)
        print("Database seeding completed successfully!")
        
        # Print summary
        user_count = User.query.count()
        template_count = BenefitTemplate.query.count()
        card_count = CardBenefitTemplate.query.count()
        
        print(f"\nSummary:")
        print(f"- Users: {user_count}")
        print(f"- Benefit templates: {template_count}")
        print(f"- Card templates: {card_count}")
        print(f"- Banks: {len(CREDIT_CARD_DATA)}")
        print(f"- Total cards: {sum(len(cards) for cards in CREDIT_CARD_DATA.values())}")


def get_available_cards():
    """Get list of available credit cards for selection."""
    
    app = create_app()
    
    with app.app_context():
        cards = CardBenefitTemplate.query.all()
        return [card.to_dict() for card in cards]


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "users":
            # Seed only users
            app = create_app()
            with app.app_context():
                seed_users()
        elif command == "benefits":
            # Seed only benefit templates
            app = create_app()
            with app.app_context():
                seed_benefit_templates()
        elif command == "all":
            # Seed everything (default)
            seed_all()
        else:
            print("Usage: python seed_data.py [users|benefits|all]")
            print("  users    - Seed only user accounts")
            print("  benefits - Seed only benefit templates")  
            print("  all      - Seed users and benefit templates (default)")
    else:
        # Default: seed everything
        seed_all()