# /src/app/security/__init__.py
"""
Security Package — v3.0

Paquete de seguridad del backend DemeArizOil.

Este módulo actúa como punto de entrada único para todas las
funcionalidades relacionadas con seguridad, incluyendo:

- Creación y decodificación de tokens JWT
- Middleware de autenticación JWT para Flask
- Hashing y verificación de contraseñas

Objetivos:
- Centralizar imports de seguridad
- Evitar dependencias directas a submódulos internos
- Facilitar el uso correcto del sistema de seguridad

IMPORTANTE:
- Otros módulos del proyecto DEBEN importar desde aquí
  y no desde archivos internos concretos.
- Esto permite refactorizar la implementación interna
  sin afectar al resto del código.

Referencia normativa:
- architecture_v3.0.md
- security_v3.0.md
"""

# ============================================================
# JWT
# ============================================================

from .jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

# ============================================================
# MIDDLEWARE
# ============================================================

from .middleware import jwt_middleware

# ============================================================
# PASSWORDS
# ============================================================

from .password import (
    hash_password,
    verify_password,
)

# ============================================================
# API PÚBLICA DEL PAQUETE
# ============================================================

__all__ = [
    # JWT
    "create_access_token",
    "create_refresh_token",
    "decode_token",

    # Middleware
    "jwt_middleware",

    # Passwords
    "hash_password",
    "verify_password",
]

# /src/app/security/__init__.py
