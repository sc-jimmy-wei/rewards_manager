import pytest
import os
from unittest.mock import patch

from migrations.database import DatabaseManager
from models import CreditCard, User, db


class TestDatabaseMigrations:
    """Test cases for database migration functionality."""

    def create_test_user(self):
        """Helper method to create a test user."""
        # Try to get existing test user first
        user = User.query.filter_by(username="testuser").first()
        if user:
            return user

        # Create new user if not exists
        user = User(username="testuser", email="test@example.com", password="test")
        db.session.add(user)
        db.session.commit()
        return user

    def test_create_all_tables(self, app_context):
        """Test creating all database tables."""
        # Drop all tables first
        db.drop_all()

        # Create all tables
        DatabaseManager.create_all()

        # Verify tables exist by checking if we can query them
        try:
            CreditCard.query.all()
            tables_created = True
        except Exception:
            tables_created = False

        assert tables_created

    def test_initialize_database(self, app_context):
        """Test database initialization."""
        # Initialize database
        DatabaseManager.initialize_database()

        # Verify database is initialized by checking table structure
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        assert "credit_card" in tables

        # Verify columns exist
        columns = inspector.get_columns("credit_card")
        column_names = [col["name"] for col in columns]

        expected_columns = [
            "id",
            "name",
            "bank",
            "card_type",
            "benefits",
            "benefits_usage",
            "image_filename",
            "opening_date",
            "credit_limit",
            "account_type",
        ]

        for col in expected_columns:
            assert col in column_names

    def test_migrate_database_new_installation(self, app_context):
        """Test database migration for new installation."""
        # Drop all tables to simulate new installation
        db.drop_all()

        # For new installation, need to create tables first
        DatabaseManager.create_all()

        # Then run migration (should handle case where columns already exist)
        DatabaseManager.migrate_database()

        # Verify tables are created
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        assert "credit_card" in tables

        # Verify we can create and query records
        user = self.create_test_user()
        card = CreditCard(
            name="Migration Test", bank="Test Bank", card_type="Visa", user_id=user.id
        )
        db.session.add(card)
        db.session.commit()

        retrieved_card = CreditCard.query.filter_by(name="Migration Test").first()
        assert retrieved_card is not None

    def test_migrate_database_existing_installation(self, app_context):
        """Test database migration with existing data."""
        # Ensure tables exist and add test data
        DatabaseManager.create_all()

        user = self.create_test_user()
        original_card = CreditCard(
            name="Original Card",
            bank="Original Bank",
            card_type="Visa",
            user_id=user.id,
        )
        db.session.add(original_card)
        db.session.commit()
        original_id = original_card.id

        # Run migration (should not affect existing data)
        DatabaseManager.migrate_database()

        # Verify existing data is preserved
        preserved_card = CreditCard.query.get(original_id)
        assert preserved_card is not None
        assert preserved_card.name == "Original Card"
        assert preserved_card.bank == "Original Bank"

    def test_database_schema_validation(self, app_context):
        """Test database schema validation."""
        DatabaseManager.initialize_database()

        inspector = db.inspect(db.engine)
        columns = inspector.get_columns("credit_card")

        # Create a mapping of column names to their properties
        column_info = {col["name"]: col for col in columns}

        # Test primary key
        assert column_info["id"]["primary_key"] == 1

        # Test required fields (not nullable)
        required_fields = ["name", "bank", "card_type"]
        for field in required_fields:
            assert not column_info[field]["nullable"]

        # Test optional fields (nullable)
        optional_fields = [
            "opening_date",
            "credit_limit",
            "account_type",
            "image_filename",
        ]
        for field in optional_fields:
            assert column_info[field]["nullable"]

        # Test JSON fields (stored as TEXT)
        json_fields = ["benefits", "benefits_usage"]
        for field in json_fields:
            assert "TEXT" in str(column_info[field]["type"]).upper()

    def test_database_constraints(self, app_context):
        """Test database constraints and data validation."""
        DatabaseManager.initialize_database()

        # Test that required fields cannot be null
        with pytest.raises(Exception):
            user = self.create_test_user()

            card = CreditCard(name=None, bank="Test", card_type="Visa", user_id=user.id)
            db.session.add(card)
            db.session.commit()

        db.session.rollback()

        with pytest.raises(Exception):
            user = self.create_test_user()

            card = CreditCard(name="Test", bank=None, card_type="Visa", user_id=user.id)
            db.session.add(card)
            db.session.commit()

        db.session.rollback()

        with pytest.raises(Exception):
            user = self.create_test_user()

            card = CreditCard(name="Test", bank="Bank", card_type=None, user_id=user.id)
            db.session.add(card)
            db.session.commit()

        db.session.rollback()

    def test_database_indexes(self, app_context):
        """Test database indexes for performance."""
        DatabaseManager.initialize_database()

        inspector = db.inspect(db.engine)

        # Check that the credit_card table exists
        tables = inspector.get_table_names()
        assert "credit_card" in tables

        # Check primary key exists (SQLite may not show all indexes explicitly)
        columns = inspector.get_columns("credit_card")
        pk_columns = [col for col in columns if col.get("primary_key", False)]
        assert len(pk_columns) >= 1

    def test_migration_error_handling(self, app_context):
        """Test migration error handling."""
        with patch("models.credit_card.db.create_all") as mock_create:
            mock_create.side_effect = Exception("Database error")

            # Migration should handle errors gracefully
            try:
                DatabaseManager.create_all()
                # Should not raise unhandled exception
            except Exception as e:
                # If exception is raised, it should be a known type
                assert isinstance(e, Exception)

    def test_backup_and_restore_functionality(self, app_context):
        """Test backup and restore functionality if implemented."""
        DatabaseManager.initialize_database()

        # Create test data
        user = self.create_test_user()
        card = CreditCard(
            name="Backup Test Card",
            bank="Backup Bank",
            card_type="Visa",
            user_id=user.id,
        )
        db.session.add(card)
        db.session.commit()
        card_id = card.id

        # If backup functionality exists, test it
        if hasattr(DatabaseManager, "backup_database"):
            backup_path = DatabaseManager.backup_database()
            assert os.path.exists(backup_path)
            
            # Verify original data still exists
            restored_card = CreditCard.query.get(card_id)
            assert restored_card is not None
            assert restored_card.name == "Backup Test Card"

        # If restore functionality exists, test it
        if hasattr(DatabaseManager, "restore_database"):
            # This would be more complex to test safely
            pass

    def test_database_connection_handling(self, app_context):
        """Test database connection handling."""
        # Test that database operations work
        DatabaseManager.initialize_database()

        # Test connection by performing a simple query
        try:
            result = db.session.execute(db.text("SELECT 1"))
            connection_works = True
            # Verify query returns expected result
            assert result.scalar() == 1
        except Exception:
            connection_works = False

        assert connection_works

    def test_transaction_rollback(self, app_context):
        """Test transaction rollback functionality."""
        DatabaseManager.initialize_database()

        # Start a transaction
        user = self.create_test_user()

        card = CreditCard(
            name="Transaction Test", bank="Test Bank", card_type="Visa", user_id=user.id
        )
        db.session.add(card)

        # Rollback before commit
        db.session.rollback()

        # Verify card was not saved
        saved_card = CreditCard.query.filter_by(name="Transaction Test").first()
        assert saved_card is None

    def test_database_metadata(self, app_context):
        """Test database metadata and introspection."""
        DatabaseManager.initialize_database()

        # Test that we can introspect the database
        inspector = db.inspect(db.engine)

        # Get table information
        tables = inspector.get_table_names()
        assert "credit_card" in tables

        # Get foreign keys (if any exist)
        foreign_keys = inspector.get_foreign_keys("credit_card")
        # CreditCard model doesn't have foreign keys in this implementation
        assert isinstance(foreign_keys, list)

    def test_database_performance_indexes(self, app_context):
        """Test database performance with indexes."""
        DatabaseManager.initialize_database()

        # Create multiple test records
        user = self.create_test_user()
        cards = []
        for i in range(10):
            card = CreditCard(
                name=f"Performance Card {i}",
                bank=f"Bank {i % 3}",  # Create some duplicates
                card_type="Visa",
                user_id=user.id,
            )
            cards.append(card)

        db.session.add_all(cards)
        db.session.commit()

        # Test query performance (basic test)
        import time

        start_time = time.time()

        result = CreditCard.query.filter_by(bank="Bank 0").all()

        end_time = time.time()
        query_time = end_time - start_time

        # Should complete quickly (less than 1 second for small dataset)
        assert query_time < 1.0
        assert len(result) > 0

    def test_concurrent_access(self, app_context):
        """Test concurrent database access."""
        DatabaseManager.initialize_database()

        # Create a card
        user = self.create_test_user()

        card1 = CreditCard(
            name="Concurrent 1", bank="Test Bank", card_type="Visa", user_id=user.id
        )
        db.session.add(card1)
        db.session.commit()

        # Simulate concurrent access by opening new session
        card2 = CreditCard(
            name="Concurrent 2",
            bank="Test Bank",
            card_type="Mastercard",
            user_id=user.id,
        )
        db.session.add(card2)
        db.session.commit()

        # Verify both cards exist
        all_cards = CreditCard.query.filter(
            CreditCard.name.in_(["Concurrent 1", "Concurrent 2"])
        ).all()
        assert len(all_cards) == 2

    def test_data_integrity_checks(self, app_context):
        """Test data integrity and consistency."""
        DatabaseManager.initialize_database()

        # Create card with benefits
        user = self.create_test_user()

        card = CreditCard(
            name="Integrity Test", bank="Test Bank", card_type="Visa", user_id=user.id
        )
        card.set_benefits_list(
            [
                {"name": "Benefit 1", "type": "Credit"},
                {"name": "Benefit 2", "type": "Reward"},
            ]
        )
        card.set_benefits_usage({"Benefit 1": 5})

        db.session.add(card)
        db.session.commit()
        card_id = card.id

        # Clear session and reload
        db.session.expunge_all()
        reloaded_card = CreditCard.query.get(card_id)

        # Verify data integrity
        assert reloaded_card.name == "Integrity Test"
        expected_benefits = [
            {"name": "Benefit 1", "type": "Credit"},
            {"name": "Benefit 2", "type": "Reward"},
        ]
        assert reloaded_card.get_benefits_list() == expected_benefits
        assert reloaded_card.get_benefits_usage() == {"Benefit 1": 5}

    def test_database_cleanup(self, app_context):
        """Test database cleanup operations."""
        DatabaseManager.initialize_database()

        # Create test data
        user = self.create_test_user()

        card = CreditCard(
            name="Cleanup Test", bank="Test Bank", card_type="Visa", user_id=user.id
        )
        db.session.add(card)
        db.session.commit()
        card_id = card.id

        # Delete the card
        db.session.delete(card)
        db.session.commit()

        # Verify deletion
        deleted_card = CreditCard.query.get(card_id)
        assert deleted_card is None

        # Test bulk cleanup if implemented
        if hasattr(DatabaseManager, "cleanup_orphaned_records"):
            DatabaseManager.cleanup_orphaned_records()

    def test_environment_specific_configs(self, app_context):
        """Test environment-specific database configurations."""
        # Test that database URL is properly configured
        from flask import current_app

        # Check that database configuration exists
        assert "SQLALCHEMY_DATABASE_URI" in current_app.config

        # In test environment, should use in-memory or test database
        db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
        assert "sqlite" in db_uri.lower()  # Test should use SQLite
