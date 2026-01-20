# /src/app/core/exceptions/handlers.py
"""
Handlers globales de excepciones para Flask.

Convierte:
- Excepciones propias (BaseAppException) → JSON consistente
- HTTPException (Werkzeug) → JSON consistente
- Errores inesperados → 500 genérico + log con traceback

Nota:
- Los logs de ERROR terminarán en app.log y exceptions.log (por configuración de handlers).
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException

from src.app.core.logging import get_logger
from .base import BaseAppException

logger = get_logger(__name__)

# ------------------------------------------------------------
# Registro de handlers
# ------------------------------------------------------------

def register_exception_handlers(app) -> None:
    """
    Registra handlers de errores en la app Flask.

    Args:
        app: instancia de Flask.
    """

    # --------------------------------------------------------
    # Excepciones del dominio (BaseAppException)
    # --------------------------------------------------------
    @app.errorhandler(BaseAppException)
    def handle_base_exception(e: BaseAppException):
        """
        Handler para excepciones controladas del dominio.
        """
        logger.error(f"[{e.status_code}] {e.message}")
        return jsonify({"error": e.error_name, "message": e.message}), e.status_code

    # --------------------------------------------------------
    # Excepciones HTTP estándar (Werkzeug)
    # --------------------------------------------------------
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        """
        Handler para errores HTTP (404, 405, etc.) generados por Flask/Werkzeug.
        """
        logger.warning(f"HTTPException {e.code}: {e.description}")
        return jsonify({"error": e.name, "message": e.description}), e.code

    # --------------------------------------------------------
    # Excepciones no controladas
    # --------------------------------------------------------
    @app.errorhandler(Exception)
    def handle_unexpected_exception(e: Exception):
        """
        Handler para errores no previstos.
        """
        logger.exception("Unexpected server error")
        return jsonify({"error": "ServerError", "message": "Unexpected error"}), 500
# /src/app/core/exceptions/handlers.py