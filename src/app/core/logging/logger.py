# /src/app/core/logging/logger.py
"""
Sistema centralizado de logging del backend DemeArizOil.

Características:
- Un único sistema de logging para toda la aplicación.
- Dos archivos de salida:
  - app.log        → INFO y superiores
  - exceptions.log → ERROR y superiores
- Rotación automática por tamaño.
- Todos los módulos escriben a través del logger raíz.
"""

import logging
from logging.handlers import RotatingFileHandler
import os

# ------------------------------------------------------------
# Configuración básica de archivos de log
# ------------------------------------------------------------

LOG_DIR = "logs"
APP_LOG = "app.log"
EXCEPTIONS_LOG = "exceptions.log"

# Aseguramos que la carpeta de logs existe
os.makedirs(LOG_DIR, exist_ok=True)

# ------------------------------------------------------------
# Formato común para todos los logs del sistema
# ------------------------------------------------------------

_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "%Y-%m-%d %H:%M:%S"
)

# ------------------------------------------------------------
# Creación de handlers (uso interno)
# ------------------------------------------------------------

def _create_handler(filename: str, level: int) -> RotatingFileHandler:
    """
    Crea un RotatingFileHandler configurado.

    level es un umbral de severidad:
    - DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50
    Regla: un handler con level=X escribe solo mensajes con nivel >= X.
    Ejemplos:
    - level=INFO  → INFO, WARNING, ERROR, CRITICAL
    - level=ERROR → ERROR, CRITICAL

    Args:
        filename: Nombre del archivo dentro de LOG_DIR (ej: "app.log").
        level: Umbral mínimo de severidad que este handler registrará.

    Returns:
        RotatingFileHandler configurado.
    """
    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, filename),
        maxBytes=1_000_000,   # 1 MB por archivo
        backupCount=5         # Mantener hasta 5 archivos antiguos
    )
    handler.setLevel(level)
    handler.setFormatter(_formatter)
    return handler

# ------------------------------------------------------------
# Inicialización global del logging (UNA sola vez)
# ------------------------------------------------------------

def setup_logging() -> None:
    """
    Inicializa el sistema de logging global de la aplicación.

    Esta función:
    - Configura el logger raíz.
    - Añade los handlers de app.log y exceptions.log.
    - Evita configuraciones duplicadas.

    DEBE llamarse:
    - Una sola vez
    - Al arrancar la aplicación (en main.py)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Evitar añadir handlers duplicados (por imports repetidos)
    if root_logger.handlers:
        return

    # Log general de la aplicación (INFO y superiores)
    root_logger.addHandler(_create_handler(APP_LOG, logging.INFO))

    # Log exclusivo de errores (ERROR y superiores)
    root_logger.addHandler(_create_handler(EXCEPTIONS_LOG, logging.ERROR))

# ------------------------------------------------------------
# Obtención de loggers lógicos por módulo
# ------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """
    Devuelve un logger lógico identificado por nombre.

    Importante:
    - Este método NO crea archivos.
    - NO añade handlers.
    - El logger obtenido propaga sus mensajes al logger raíz.

    Uso recomendado:
        logger = get_logger(__name__)

    :param name: Nombre del módulo (normalmente __name__)
    :return: Logger configurado
    """
    return logging.getLogger(name)
# /src/app/core/logging/logger.py