import json
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()


class CreditCard(db.Model):
    """Credit Card model for storing credit card information."""

    # Table columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bank = db.Column(db.String(100), nullable=False)
    card_type = db.Column(db.String(50), nullable=False)
    benefits = db.Column(db.Text, nullable=True)
    benefits_usage = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)
    opening_date = db.Column(db.Date, nullable=True)
    credit_limit = db.Column(db.Integer, nullable=True)
    account_type = db.Column(db.String(20), nullable=True)

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(
        self,
        name,
        bank,
        card_type,
        user_id,
        benefits=None,
        image_filename=None,
        opening_date=None,
        credit_limit=None,
        account_type=None,
    ):
        """Initialize a new CreditCard instance."""
        self.name = name
        self.bank = bank
        self.card_type = card_type
        self.user_id = user_id
        self.benefits = benefits or "[]"
        self.benefits_usage = "{}"
        self.image_filename = image_filename
        self.opening_date = opening_date
        self.credit_limit = credit_limit
        self.account_type = account_type

    def get_benefits_list(self):
        """Get benefits as a Python list with backward compatibility."""
        try:
            benefits_data = json.loads(self.benefits) if self.benefits else []
            # Handle backward compatibility - convert old string format to new dict format
            if benefits_data and isinstance(benefits_data[0], str):
                # Old format: ["benefit1", "benefit2"]
                # Convert to new format: [{"name": "benefit1", "type": "Credit"}, {"name": "benefit2", "type": "Credit"}]
                return [
                    {"name": benefit, "type": "Credit"} for benefit in benefits_data
                ]
            return benefits_data
        except (json.JSONDecodeError, TypeError):
            return []

    def get_benefits_usage(self):
        """Get benefits usage as a Python dictionary."""
        try:
            return json.loads(self.benefits_usage) if self.benefits_usage else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_benefits_list(self, benefits_list):
        """Set benefits from a Python list. Expects list of dicts with 'name' and 'type' keys."""
        self.benefits = json.dumps(benefits_list)

    def get_credit_benefits(self):
        """Get only Credit type benefits."""
        return [
            benefit
            for benefit in self.get_benefits_list()
            if benefit.get("type") == "Credit"
        ]

    def get_reward_benefits(self):
        """Get only Reward type benefits."""
        return [
            benefit
            for benefit in self.get_benefits_list()
            if benefit.get("type") == "Reward"
        ]

    def set_benefits_usage(self, usage_dict):
        """Set benefits usage from a Python dictionary."""
        self.benefits_usage = json.dumps(usage_dict)

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "bank": self.bank,
            "card_type": self.card_type,
            "benefits": self.get_benefits_list(),
            "benefits_usage": self.get_benefits_usage(),
            "image_filename": self.image_filename,
            "opening_date": self.opening_date.isoformat()
            if self.opening_date
            else None,
            "credit_limit": self.credit_limit,
            "account_type": self.account_type,
        }

    def __repr__(self):
        """String representation of the CreditCard."""
        return f"<CreditCard {self.bank} {self.name}>"
