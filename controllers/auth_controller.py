from datetime import datetime, timedelta
import secrets
from flask import session
from flask_login import login_user, logout_user, current_user
from models import db, User


class AuthController:
    """Controller for user authentication and authorization."""

    @staticmethod
    def login_user_by_credentials(username, password, remember=False):
        """
        Authenticate user by username/email and password.

        Args:
            username (str): Username or email
            password (str): Plain text password
            remember (bool): Whether to remember the user session

        Returns:
            tuple: (success: bool, user: User|None, message: str)
        """
        try:
            # Find user by username or email
            user = User.query.filter(
                (User.username == username) | (User.email == username)
            ).first()

            if not user:
                return False, None, "Invalid username or password"

            if not user.is_active:
                return False, None, "Account is disabled"

            if not user.check_password(password):
                return False, None, "Invalid username or password"

            # Update last login
            user.update_last_login()
            db.session.commit()

            # Login user with Flask-Login
            login_user(user, remember=remember)

            return True, user, f"Welcome back, {user.get_full_name()}!"

        except Exception as e:
            db.session.rollback()
            return False, None, f"Login failed: {str(e)}"

    @staticmethod
    def register_user(username, email, password, first_name=None, last_name=None):
        """
        Register a new user account.

        Args:
            username (str): Unique username
            email (str): Unique email address
            password (str): Plain text password
            first_name (str, optional): First name
            last_name (str, optional): Last name

        Returns:
            tuple: (success: bool, user: User|None, message: str)
        """
        try:
            # Check if username already exists
            if User.query.filter_by(username=username).first():
                return False, None, "Username already exists"

            # Check if email already exists
            if User.query.filter_by(email=email).first():
                return False, None, "Email already registered"

            # Create new user
            user = User(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role="user",  # New users get 'user' role by default
            )

            db.session.add(user)
            db.session.commit()

            return True, user, "Account created successfully! Please log in."

        except Exception as e:
            db.session.rollback()
            return False, None, f"Registration failed: {str(e)}"

    @staticmethod
    def logout_current_user():
        """
        Logout the current user.

        Returns:
            str: Success message
        """
        user_name = (
            current_user.get_full_name() if current_user.is_authenticated else "User"
        )
        logout_user()
        session.clear()
        return f"Goodbye, {user_name}!"

    @staticmethod
    def validate_registration_form(form_data):
        """
        Validate registration form data.

        Args:
            form_data: Form data object

        Returns:
            list: List of validation errors
        """
        errors = []

        # Required fields
        if not form_data.get("username", "").strip():
            errors.append("Username is required")
        elif len(form_data.get("username", "").strip()) < 3:
            errors.append("Username must be at least 3 characters long")
        elif len(form_data.get("username", "").strip()) > 50:
            errors.append("Username must be less than 50 characters")

        if not form_data.get("email", "").strip():
            errors.append("Email is required")
        elif "@" not in form_data.get("email", "") or "." not in form_data.get(
            "email", ""
        ):
            errors.append("Please enter a valid email address")

        if not form_data.get("password", ""):
            errors.append("Password is required")
        elif len(form_data.get("password", "")) < 6:
            errors.append("Password must be at least 6 characters long")

        if form_data.get("password") != form_data.get("confirm_password"):
            errors.append("Passwords do not match")

        # Optional fields validation
        first_name = form_data.get("first_name", "").strip()
        if first_name and len(first_name) > 50:
            errors.append("First name must be less than 50 characters")

        last_name = form_data.get("last_name", "").strip()
        if last_name and len(last_name) > 50:
            errors.append("Last name must be less than 50 characters")

        return errors

    @staticmethod
    def validate_login_form(form_data):
        """
        Validate login form data.

        Args:
            form_data: Form data object

        Returns:
            list: List of validation errors
        """
        errors = []

        if not form_data.get("username", "").strip():
            errors.append("Username or email is required")

        if not form_data.get("password", ""):
            errors.append("Password is required")

        return errors

    @staticmethod
    def generate_password_reset_token(email):
        """
        Generate a password reset token for a user.

        Args:
            email (str): User's email address

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                # Don't reveal if email exists or not for security
                return (
                    True,
                    "If an account with that email exists, password reset instructions have been sent.",
                )

            # Generate secure token
            token = secrets.token_urlsafe(32)

            # Set token and expiration (1 hour from now)
            user.reset_token = token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)

            db.session.commit()

            # In a real application, you would send an email here
            # For now, we'll just return the token for demonstration
            return True, f"Password reset token generated: {token}"

        except Exception as e:
            db.session.rollback()
            return False, f"Failed to generate reset token: {str(e)}"

    @staticmethod
    def reset_password_with_token(token, new_password):
        """
        Reset password using a valid token.

        Args:
            token (str): Password reset token
            new_password (str): New password

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            user = User.query.filter_by(reset_token=token).first()

            if not user:
                return False, "Invalid or expired reset token"

            if (
                not user.reset_token_expires
                or user.reset_token_expires < datetime.utcnow()
            ):
                return False, "Reset token has expired"

            # Update password and clear reset token
            user.set_password(new_password)
            user.reset_token = None
            user.reset_token_expires = None

            db.session.commit()

            return (
                True,
                "Password has been reset successfully. Please log in with your new password.",
            )

        except Exception as e:
            db.session.rollback()
            return False, f"Failed to reset password: {str(e)}"

    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID for Flask-Login user loader.

        Args:
            user_id (str): User ID

        Returns:
            User|None: User object or None
        """
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None
