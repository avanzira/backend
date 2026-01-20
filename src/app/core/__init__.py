# /src/app/core/__init__.py
"""Core package — v3.0

Punto de entrada único al núcleo de la aplicación.

Este módulo expone la API pública de `core` para facilitar imports
limpios y coherentes en el resto del proyecto.
"""

# ============================================================
# enum DE DOMINIO
# ============================================================

from src.app.core.enum import UserRole, DocumentStatus, StockMovementType

# ============================================================
# CONFIGURACIÓN
# ============================================================

from src.app.core.config.settings import settings

# ============================================================
# LOGGING
# ============================================================

from src.app.core.logging import get_logger, setup_logging

# ============================================================
# HANDLERS DE EXCEPCIONES
# ============================================================

from src.app.core.exceptions import register_exception_handlers

# ============================================================
# EXCEPCIONES
# ============================================================

from src.app.core.exceptions import (
    BaseAppException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    ServerErrorException,
)

# ============================================================
# UTILIDADES
# ============================================================

from src.app.core.utils.datetime_utils import dt_to_iso_z, now_epoch, future_epoch

# ============================================================
# DATABASE
# ============================================================

from src.app.core.config.database import db_session


# /src/app/core/__init__.py