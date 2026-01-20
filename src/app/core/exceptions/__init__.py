# /src/app/core/exceptions/__init__.py
"""
Package de excepciones del core.

Expone:
- Excepciones de dominio (para services y controllers)
- Registro de handlers para Flask
"""

from .base import (
    BaseAppException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    ConflictException,
    ServerErrorException,
)
from .handlers import register_exception_handlers

__all__ = [
    "BaseAppException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "ConflictException",
    "ServerErrorException",
    "register_exception_handlers",
]

# /src/app/core/exceptions/__init__.py
