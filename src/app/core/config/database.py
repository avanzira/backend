# /src/app/core/config/database.py 
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from src.app.core.config.settings import settings

# Best practice: engine único y session scoped
DATABASE_URL = f"sqlite:///{settings.DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# ------------------------------------------------------
# IMPORTANTE:
# Registrar TODOS los modelos antes de crear la sesión.
# Base importa user, products, suppliers, etc.
# ------------------------------------------------------
from src.app.db.base import Base

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
db_session = scoped_session(SessionLocal)

# Hook para cerrar sesión en teardown
def init_app(app):
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

# /src/app/core/config/database.py 