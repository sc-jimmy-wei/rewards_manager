from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .credit_card import db


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Authentication fields
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile fields
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)

    # Role and status
    role = db.Column(db.String(20), nullable=False, default="user")  # 'user' or 'admin'
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login = db.Column(db.DateTime, nullable=True)

    # Password reset fields
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    # Relationships
    credit_cards = db.relationship(
        "CreditCard", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    airline_programs = db.relationship(
        "AirlineProgram", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(
        self, username, email, password, first_name=None, last_name=None, role="user"
    ):
        """Initialize a new User instance."""
        self.username = username
        self.email = email
        self.set_password(password)
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.is_active = True

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Check if the user has admin role."""
        return self.role == "admin"

    def get_full_name(self):
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username

    def get_id(self):
        """Get user ID for Flask-Login."""
        return str(self.id)

    def is_authenticated(self):
        """Check if user is authenticated (required by Flask-Login)."""
        return True

    def is_anonymous(self):
        """Check if user is anonymous (required by Flask-Login)."""
        return False

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.get_full_name(),
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self):
        """String representation of the User."""
        return f"<User {self.username} ({self.role})>"
