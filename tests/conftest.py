# /src/app/tests/conftest.py
import os
import pytest
from datetime import datetime

from src.app.core.config.settings import settings
from src.app.main import create_app
from src.app.init_data import init_data
from src.app.db.base import Base
from src.app.core.config.database import engine, db_session, SessionLocal

# ------------------------------------------------------------
# CONFIGURACIÓN GLOBAL DE TESTING
# ------------------------------------------------------------

TEST_DATABASE_PATH = "/tmp/demearizoil_test.db"

@pytest.fixture(scope="session", autouse=True)
def test_settings():
    os.environ["DATABASE_PATH"] = TEST_DATABASE_PATH
    settings.DATABASE_PATH = TEST_DATABASE_PATH
    yield
    if os.path.exists(TEST_DATABASE_PATH):
        os.remove(TEST_DATABASE_PATH)

# ------------------------------------------------------------
# APP + DB LIMPIA POR TEST
# ------------------------------------------------------------

@pytest.fixture(scope="function")
def app():
    if os.path.exists(TEST_DATABASE_PATH):
        os.remove(TEST_DATABASE_PATH)

    application = create_app(testing=True)
    Base.metadata.create_all(bind=engine)
    init_data()

    with application.app_context():
        yield application

    Base.metadata.drop_all(bind=engine)
    db_session.remove()

# ------------------------------------------------------------
# CLIENTE HTTP
# ------------------------------------------------------------

@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

# ------------------------------------------------------------
# SESIÓN SQLALCHEMY
# ------------------------------------------------------------

@pytest.fixture(scope="function")
def session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------------------------------------
# FIXTURES DE USUARIOS (OPT-IN)
# ------------------------------------------------------------

from src.app.models.user import User
from src.app.security.password import hash_password
from src.app.security.jwt import create_access_token
from src.app.core import UserRole

@pytest.fixture
def admin_user(session):
    user = session.query(User).filter_by(username="admin").first()
    if user:
        return user

@pytest.fixture
def admin_token(admin_user):
    return create_access_token(admin_user)
# /src/app/tests/conftest.py
