# /src/app/main.py
"""
Punto de entrada principal del backend DemeArizOil.

Responsabilidades de este módulo:
- Crear y configurar la aplicación Flask.
- Inicializar logging, base de datos y datos iniciales.
- Registrar middleware, excepciones y rutas.
- Exponer la aplicación WSGI.
"""

from flask import Flask

# ------------------------------------------------------------
# Importaciones del core del proyecto
# ------------------------------------------------------------
from src.app.core import get_logger, setup_logging, register_exception_handlers, settings

# ------------------------------------------------------------
# Importaciones de base de datos (infraestructura)
# ------------------------------------------------------------
from src.app.core.config.database import engine, init_app
from src.app.db.base import Base

# ------------------------------------------------------------
# Importaciones de la capa API y seguridad
# ------------------------------------------------------------
from src.app.api.api_router import api_router
from src.app.security.middleware import jwt_middleware

# ------------------------------------------------------------
# Datos iniciales
# ------------------------------------------------------------
from src.app.init_data import init_data

# ------------------------------------------------------------
# Factory de la aplicación Flask
# ------------------------------------------------------------
def create_app(testing: bool = False) -> Flask:
    """
    Crea y configura la aplicación Flask.

    Este método:
    - Inicializa logging (una sola vez).
    - Configura Flask y la base de datos.
    - Crea las tablas.
    - Inserta datos iniciales.
    - Registra middleware, handlers y rutas.

    :param testing: Indica si la app se ejecuta en modo testing.
    :return: Instancia configurada de Flask.
    """

    # --------------------------------------------------------
    # Inicialización del logging (OBLIGATORIO al inicio)
    # --------------------------------------------------------
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting DemeArizOil backend")

    # --------------------------------------------------------
    # Creación de la aplicación Flask
    # --------------------------------------------------------
    app = Flask(__name__)
    app.testing = testing

    # --------------------------------------------------------
    # Inicialización de la base de datos y configuración
    # --------------------------------------------------------
    init_app(app)

    # --------------------------------------------------------
    # Creación de tablas
    # --------------------------------------------------------
    Base.metadata.create_all(bind=engine)

    # --------------------------------------------------------
    # Carga de datos iniciales
    # --------------------------------------------------------
    if not testing:
        try:
            init_data()
        except Exception:
            logger.exception("Error seeding initial data")

    # --------------------------------------------------------
    # Registro de handlers de excepciones
    # --------------------------------------------------------
    register_exception_handlers(app)

    # --------------------------------------------------------
    # Registro del middleware de seguridad JWT
    # --------------------------------------------------------
    jwt_middleware(app)

    # --------------------------------------------------------
    # Endpoint raíz (healthcheck)
    # --------------------------------------------------------
    @app.get("/")
    def root():
        """
        Endpoint de verificación de estado del backend.
        """
        return {
            "app": "DemeArizOil Backend",
            "status": "running",
        }, 200

    # --------------------------------------------------------
    # Registro de la API principal
    # --------------------------------------------------------
    app.register_blueprint(api_router, url_prefix="/api")

    return app

# ------------------------------------------------------------
# Exposición de la app WSGI
# ------------------------------------------------------------

app = create_app()

# ------------------------------------------------------------
# Ejecución directa (solo desarrollo)
# ------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)

# /src/app/main.py
