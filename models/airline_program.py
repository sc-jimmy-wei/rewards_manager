from .credit_card import db


class AirlineProgram(db.Model):
    """Model for airline mileage program accounts."""

    __tablename__ = "airline_program"

    id = db.Column(db.Integer, primary_key=True)
    airline_name = db.Column(db.String(100), nullable=False)
    program_name = db.Column(db.String(100), nullable=False)
    account_id = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, nullable=True, default=0)
    expiration_date = db.Column(db.Date, nullable=True)
    extension_rule = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(
        self,
        airline_name,
        program_name,
        account_id,
        user_id,
        points=0,
        expiration_date=None,
        extension_rule=None,
    ):
        """Initialize a new airline mileage program."""
        self.airline_name = airline_name
        self.program_name = program_name
        self.account_id = account_id
        self.user_id = user_id
        self.points = points or 0
        self.expiration_date = expiration_date
        self.extension_rule = extension_rule

    def to_dict(self):
        """Convert airline mileage program to dictionary."""
        return {
            "id": self.id,
            "airline_name": self.airline_name,
            "program_name": self.program_name,
            "account_id": self.account_id,
            "points": self.points,
            "expiration_date": self.expiration_date.isoformat()
            if self.expiration_date
            else None,
            "extension_rule": self.extension_rule,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        """String representation of airline mileage program."""
        return f"<AirlineProgram {self.airline_name} - {self.program_name}>"
