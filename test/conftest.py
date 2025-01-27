import pytest
from app import app as flask_app, db  # Import your Flask app and database instance
from app.todo.models import User, Tasks

@pytest.fixture
def app():
    """
    setup for pytest
    """
    flask_app.config.update({
        "TESTING": True,  # Enable test mode
        "SQLALCHEMY_DATABASE_URI": "postgresql://postgres:amit@localhost:5432/todo",  # Use the 'todo' database
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_SECRET_KEY": "test_secret",  # Use a different secret key for testing
    })

    # setting app_context()
    with flask_app.app_context():
        db.create_all()  # Create all tables
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    # THis fucntions is used to create client
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

