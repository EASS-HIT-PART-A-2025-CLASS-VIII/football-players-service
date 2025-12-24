import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlmodel import SQLModel, Session

# Use in-memory SQLite for tests with shared cache
# This allows multiple connections to share the same in-memory database
TEST_DATABASE_URL = "sqlite:///file::memory:?cache=shared&uri=true"


@pytest.fixture(scope="session")
def test_engine():
    """Create a test engine with in-memory SQLite database for the entire session."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )

    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Import models to register them with metadata
    from football_player_service.app.models import Player  # noqa: F401

    # Create all tables
    SQLModel.metadata.create_all(engine)

    yield engine


@pytest.fixture(autouse=True)
def clear_database(test_engine):
    """Clear all tables before each test."""
    # Skip clearing before session - let test_engine fixture handle setup
    yield
    # Clear after each test
    with Session(test_engine) as session:
        try:
            session.exec(text("DELETE FROM players"))
            session.commit()
        except Exception:
            # If table doesn't exist yet, that's okay
            session.rollback()


@pytest.fixture
def client(test_engine):
    """Provide a TestClient with test database override."""
    # Import main app and database module
    from football_player_service.app.main import app
    from football_player_service.app import database

    # Create the override function for get_session
    def override_get_session():
        session = Session(test_engine)
        try:
            yield session
        finally:
            session.close()

    # Override init_db to prevent production database initialization
    def override_init_db():
        """Test version that does nothing - we already created tables in test_engine."""
        pass

    # Store original functions
    original_init_db = database.init_db

    # Override both the function and the app dependency
    database.init_db = override_init_db
    app.dependency_overrides[database.get_session] = override_get_session

    # Create test client (this will trigger lifespan which now uses overridden init_db)
    test_client = TestClient(app)

    yield test_client

    # Cleanup
    database.init_db = original_init_db
    app.dependency_overrides.clear()
