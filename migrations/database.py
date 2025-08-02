from models import db, User
from sqlalchemy import inspect


class DatabaseManager:
    """Handles database operations and migrations."""

    @staticmethod
    def is_postgresql():
        """Check if the database is PostgreSQL."""
        return db.engine.dialect.name == "postgresql"

    @staticmethod
    def create_all():
        """Create all database tables."""
        db.create_all()
        print("Database tables created successfully.")

    @staticmethod
    def drop_all():
        """Drop all database tables."""
        db.drop_all()
        print("Database tables dropped successfully.")

    @staticmethod
    def migrate_database():
        """Add new columns if they don't exist (for backwards compatibility)."""
        try:
            # Use inspector to check existing columns
            inspector = inspect(db.engine)

            # Handle credit card table migrations
            if "credit_card" in inspector.get_table_names():
                existing_columns = [
                    col["name"] for col in inspector.get_columns("credit_card")
                ]

                credit_card_columns = [
                    ("image_filename", "VARCHAR(255)"),
                    ("opening_date", "DATE"),
                    ("credit_limit", "INTEGER"),
                    ("account_type", "VARCHAR(20)"),
                ]

                for column_name, column_type in credit_card_columns:
                    if column_name not in existing_columns:
                        try:
                            db.session.execute(
                                db.text(
                                    f"ALTER TABLE credit_card ADD COLUMN {column_name} {column_type}"
                                )
                            )
                            db.session.commit()
                            print(
                                f"Database migrated: Added {column_name} column to credit_card"
                            )
                        except Exception as e:
                            print(f"Migration failed for {column_name}: {e}")
                            db.session.rollback()

            # Handle user_id foreign key for existing tables
            DatabaseManager._add_user_foreign_keys()

            # Handle benefit_templates migrations
            DatabaseManager._migrate_benefit_templates()

        except Exception as e:
            print(f"Migration error: {e}")
            db.session.rollback()

    @staticmethod
    def _add_user_foreign_keys():
        """Add user_id foreign keys to existing tables."""
        try:
            # Check if users table exists using inspector
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if "users" not in tables:
                print("Users table doesn't exist yet, skipping foreign key migration")
                return

            # Check if user_id column exists in credit_card table
            credit_card_columns = [
                col["name"] for col in inspector.get_columns("credit_card")
            ]
            if "user_id" not in credit_card_columns:
                try:
                    if DatabaseManager.is_postgresql():
                        db.session.execute(
                            db.text(
                                "ALTER TABLE credit_card ADD COLUMN user_id INTEGER REFERENCES users(id)"
                            )
                        )
                    else:
                        db.session.execute(
                            db.text(
                                "ALTER TABLE credit_card ADD COLUMN user_id INTEGER"
                            )
                        )
                    db.session.commit()
                    print("Added user_id column to credit_card table")
                except Exception as e:
                    print(f"Failed to add user_id to credit_card: {e}")
                    db.session.rollback()
            else:
                print("user_id column already exists in credit_card table")

            # Check if user_id column exists in airline_program table
            airline_program_columns = [
                col["name"] for col in inspector.get_columns("airline_program")
            ]
            if "user_id" not in airline_program_columns:
                try:
                    if DatabaseManager.is_postgresql():
                        db.session.execute(
                            db.text(
                                "ALTER TABLE airline_program ADD COLUMN user_id INTEGER REFERENCES users(id)"
                            )
                        )
                    else:
                        db.session.execute(
                            db.text(
                                "ALTER TABLE airline_program ADD COLUMN user_id INTEGER"
                            )
                        )
                    db.session.commit()
                    print("Added user_id column to airline_program table")
                except Exception as e:
                    print(f"Failed to add user_id to airline_program: {e}")
                    db.session.rollback()
            else:
                print("user_id column already exists in airline_program table")

        except Exception as e:
            print(f"Error in foreign key migration: {e}")
            db.session.rollback()


    @staticmethod
    def _migrate_benefit_templates():
        """Add image_url column to benefit_templates table if it doesn't exist."""
        try:
            inspector = inspect(db.engine)
            
            if "benefit_templates" in inspector.get_table_names():
                existing_columns = [
                    col["name"] for col in inspector.get_columns("benefit_templates")
                ]
                
                if "image_url" not in existing_columns:
                    try:
                        db.session.execute(
                            db.text(
                                "ALTER TABLE benefit_templates ADD COLUMN image_url VARCHAR(500)"
                            )
                        )
                        db.session.commit()
                        print("Added image_url column to benefit_templates table")
                    except Exception as e:
                        print(f"Failed to add image_url to benefit_templates: {e}")
                        db.session.rollback()
                else:
                    print("image_url column already exists in benefit_templates table")
                
                if "reset_type" not in existing_columns:
                    try:
                        db.session.execute(
                            db.text(
                                "ALTER TABLE benefit_templates ADD COLUMN reset_type VARCHAR(20)"
                            )
                        )
                        db.session.commit()
                        print("Added reset_type column to benefit_templates table")
                    except Exception as e:
                        print(f"Failed to add reset_type to benefit_templates: {e}")
                        db.session.rollback()
                else:
                    print("reset_type column already exists in benefit_templates table")
        except Exception as e:
            print(f"Error in benefit_templates migration: {e}")
            db.session.rollback()

    @staticmethod
    def initialize_database():
        """Initialize the database with tables and migrations."""
        DatabaseManager.create_all()
        DatabaseManager.migrate_database()
        print("Database initialization completed.")
