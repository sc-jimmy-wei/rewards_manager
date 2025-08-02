#!/usr/bin/env python3
"""
PostgreSQL setup script for the Credit Rewards Manager application.

This script helps set up the database for production use with PostgreSQL.
"""

import os
import sys
from app import create_app
from models import db
from migrations import DatabaseManager


def setup_postgres_database(database_url=None):
    """Set up PostgreSQL database with all tables and default data."""

    if database_url:
        os.environ["DATABASE_URL"] = database_url

    print("Setting up PostgreSQL database...")
    print(
        f"Database URL: {os.environ.get('DATABASE_URL', 'Not set - will use default SQLite')}"
    )

    # Create app with PostgreSQL configuration
    app = create_app(
        "production"
        if "postgresql" in os.environ.get("DATABASE_URL", "")
        else "development"
    )

    with app.app_context():
        try:
            # Print database info
            print(f"Database engine: {db.engine.dialect.name}")
            print(f"Database URL: {db.engine.url}")

            # Initialize database
            print("\n=== Creating database tables ===")
            DatabaseManager.initialize_database()

            # Verify setup
            print("\n=== Verifying setup ===")
            from models import User, CreditCard, AirlineProgram

            user_count = User.query.count()
            card_count = CreditCard.query.count()
            program_count = AirlineProgram.query.count()

            print(f"Users: {user_count}")
            print(f"Credit Cards: {card_count}")
            print(f"Airline Programs: {program_count}")

            # Test user creation
            admin_user = User.query.filter_by(username="admin").first()
            test_user = User.query.filter_by(username="testuser").first()

            if admin_user:
                print(f"✓ Admin user exists: {admin_user.username} ({admin_user.role})")
            if test_user:
                print(f"✓ Test user exists: {test_user.username} ({test_user.role})")

            print("\n=== Database setup completed successfully! ===")

            return True

        except Exception as e:
            print(f"\n❌ Database setup failed: {e}")
            return False


def main():
    """Main function to handle command line arguments."""

    if len(sys.argv) > 1:
        database_url = sys.argv[1]
        print(f"Using provided database URL: {database_url}")
    else:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("No DATABASE_URL provided. Using default configuration.")
            print("\nTo use PostgreSQL, provide a database URL:")
            print(
                "python setup_postgres.py 'postgresql://username:password@localhost/dbname'"
            )
            print("\nOr set the DATABASE_URL environment variable:")
            print(
                "export DATABASE_URL='postgresql://username:password@localhost/dbname'"
            )
            print("\nProceeding with default configuration...")

    success = setup_postgres_database(database_url)

    if success:
        print("\n🎉 Setup completed successfully!")
        print("\nYou can now run the application:")
        print("python app.py")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
