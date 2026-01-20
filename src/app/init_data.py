# /src/app/init_data.py
"""
Inicialización de datos básicos del sistema (seeding).

Este módulo se ejecuta al arrancar la aplicación y garantiza que
existen los elementos mínimos para poder operar el sistema.

Características:
- Idempotente: puede ejecutarse múltiples veces sin duplicar datos.
- No depende de requests ni contexto HTTP.
- Solo se usa en el arranque de la app (main.py).

Datos que asegura:
1. Usuario administrador inicial.
2. Ubicación de stock COMPANY de DEME.
3. Cuenta de efectivo principal de DEME.
"""

from datetime import datetime, timezone

from src.app.core import settings, get_logger, UserRole
from src.app.core.config.database import db_session
from src.app.security.password import hash_password

from src.app.models.user import User
from src.app.models.stock_location import StockLocation
from src.app.models.cash_account import CashAccount

logger = get_logger(__name__)

# ------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ------------------------------------------------------------

def init_data() -> None:
    """
    Inserta datos iniciales en base de datos si no existen.

    Esta función:
    - NO borra datos existentes.
    - NO asume una base de datos vacía.
    - Puede ejecutarse en cada arranque sin efectos secundarios.

    Cualquier error aquí se considera crítico para el arranque.
    """

    # --------------------------------------------------------
    # 1. USUARIO ADMINISTRADOR
    # --------------------------------------------------------
    admin_username = getattr(settings, "INIT_ADMIN_USERNAME", "admin")
    admin_email = getattr(settings, "INIT_ADMIN_EMAIL", "admin@example.com")
    admin_password = getattr(settings, "INIT_ADMIN_PASSWORD", "admin123")

    admin = db_session.query(User).filter(User.username == admin_username).first()
    if not admin:
        admin = User(
            username=admin_username,
            email=admin_email,
            hash_password=hash_password(admin_password),
            rol=UserRole.ADMIN,
            password_changed_at=datetime.now(timezone.utc),
        )
        db_session.add(admin)
        logger.info("Created initial admin user")

    # --------------------------------------------------------
    # 2. UBICACIÓN DE STOCK COMPANY (DEME)
    # --------------------------------------------------------
    deme_stock_name = settings.DEME_STOCK_LOCATION_NAME

    deme_stock = (
        db_session.query(StockLocation)
        .filter(StockLocation.name == deme_stock_name)
        .first()
    )
    if not deme_stock:
        deme_stock = StockLocation(
            name=deme_stock_name,
        )
        db_session.add(deme_stock)
        logger.info("Created DEME COMPANY stock location")

    # --------------------------------------------------------
    # 3. CUENTA DE EFECTIVO PRINCIPAL DE DEME
    # --------------------------------------------------------
    deme_cash_name = settings.DEME_CASH_ACCOUNT_NAME

    deme_cash = (
        db_session.query(CashAccount)
        .filter(CashAccount.name == deme_cash_name)
        .first()
    )
    if not deme_cash:
        deme_cash = CashAccount(
            name=deme_cash_name,
            balance=2000,
        )
        db_session.add(deme_cash)
        logger.info("Created DEME cash account")

    # --------------------------------------------------------
    # COMMIT FINAL
    # --------------------------------------------------------
    db_session.commit()
    logger.info("Initial data check completed successfully")

# ------------------------------------------------------------
# EJECUCIÓN DIRECTA (solo desarrollo / debug)
# ------------------------------------------------------------

if __name__ == "__main__":
    init_data()
# /src/app/init_data.py
