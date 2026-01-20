# /src/app/core/logging/__init__.py
"""
Core logging package for DemeArizOil backend.

Este módulo expone una API mínima y controlada para el sistema de logging
del proyecto, evitando configuraciones duplicadas o dispersas.

Uso esperado:
- setup_logging(): se llama UNA vez al arrancar la aplicación.
- get_logger(__name__): se usa en cualquier módulo para emitir logs.
"""

# ------------------------------------------------------------
# API pública del módulo logging
# ------------------------------------------------------------

from .logger import setup_logging, get_logger

__all__ = [
    "setup_logging",
    "get_logger",
]
# /src/app/core/logging/__init__.py