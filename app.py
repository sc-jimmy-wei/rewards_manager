import os
from flask import Flask
from flask_login import LoginManager

from config import config
from models import db
from routes import credit_card_bp
from routes.airline_program_routes import airline_program_bp
from routes.auth_routes import auth_bp
from migrations import DatabaseManager
from controllers.auth_controller import AuthController


def create_app(config_name=None):
    """Application factory pattern for creating Flask app."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "error"

    @login_manager.user_loader
    def load_user(user_id):
        return AuthController.get_user_by_id(user_id)

    # Register blueprints
    app.register_blueprint(credit_card_bp)
    app.register_blueprint(airline_program_bp)
    app.register_blueprint(auth_bp)

    # Initialize database
    with app.app_context():
        DatabaseManager.initialize_database()

    return app


# Create the Flask application
app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
