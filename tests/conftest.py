import pytest
import tempfile
from PIL import Image
from io import BytesIO
from datetime import date

from app import create_app
from models import db, CreditCard, User


@pytest.fixture
def app():
    """Create a Flask application configured for testing."""
    app = create_app("testing")
    app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp()
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Create and login test user for protected routes

            test_user = User.query.filter_by(username="testuser").first()
            if test_user:
                with client.session_transaction() as sess:
                    sess["_user_id"] = str(test_user.id)
                    sess["_fresh"] = True

            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def app_context(app):
    """Create an application context for testing."""
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_card():
    """Create a sample credit card for testing."""
    # Get or create test user
    test_user = User.query.filter_by(username="testuser").first()
    if not test_user:
        test_user = User(username="testuser", email="test@example.com", password="test")
        db.session.add(test_user)
        db.session.commit()

    card = CreditCard(
        name="Test Card",
        bank="Test Bank",
        card_type="Visa",
        opening_date=date(2024, 1, 15),
        credit_limit=5000,
        account_type="Personal",
        user_id=test_user.id,
    )
    card.set_benefits_list(["Cash back", "Travel points"])
    db.session.add(card)
    db.session.commit()
    return card


@pytest.fixture
def sample_image():
    """Create a sample image file for testing uploads."""
    # Create a simple test image
    image = Image.new("RGB", (100, 100), color="red")
    img_buffer = BytesIO()
    image.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    return img_buffer


@pytest.fixture
def multiple_cards():
    """Create multiple credit cards for testing."""
    # Get or create test user
    test_user = User.query.filter_by(username="testuser").first()
    if not test_user:
        test_user = User(username="testuser", email="test@example.com", password="test")
        db.session.add(test_user)
        db.session.commit()

    cards = [
        CreditCard(
            name="Chase Sapphire",
            bank="Chase",
            card_type="Visa",
            opening_date=date(2024, 1, 15),
            credit_limit=10000,
            account_type="Personal",
            user_id=test_user.id,
        ),
        CreditCard(
            name="Amex Gold",
            bank="American Express",
            card_type="American Express",
            opening_date=date(2023, 6, 1),
            credit_limit=25000,
            account_type="Personal",
            user_id=test_user.id,
        ),
        CreditCard(
            name="Discover It",
            bank="Discover",
            card_type="Discover",
            opening_date=date(2023, 12, 10),
            credit_limit=7500,
            account_type="Personal",
            user_id=test_user.id,
        ),
    ]

    # Set benefits for each card
    cards[0].set_benefits_list(["2x travel", "1.25x redemption"])
    cards[1].set_benefits_list(["4x dining", "4x groceries", "3x flights"])
    cards[2].set_benefits_list(["5% rotating categories", "Cashback match"])

    for card in cards:
        db.session.add(card)
    db.session.commit()
    return cards
