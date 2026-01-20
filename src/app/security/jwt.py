# /src/app/security/jwt.py
"""
JWT Utilities — v3.0

Utilidades centralizadas para la creación y validación de tokens JWT
en el backend DemeArizOil.

Responsabilidades de este módulo:
- Emitir access tokens y refresh tokens
- Definir el payload estándar del proyecto
- Normalizar timestamps de forma consistente
- Garantizar compatibilidad con frontend y middleware

Decisiones clave de diseño:
- Se utiliza UN ÚNICO SECRET para access y refresh tokens
- El access token incluye un objeto `user` para consumo directo del frontend
- El refresh token NO está pensado para ser leído por el frontend
- Todos los timestamps se normalizan usando datetime_utils.py

IMPORTANTE:
- Este módulo NO valida permisos ni roles
- Este módulo NO accede a la base de datos
- Este módulo NO contiene lógica de negocio

Referencia normativa:
- security_v3.0.md
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict

import jwt

from src.app.core.config.settings import settings
from src.app.core.utils.datetime_utils import (
    dt_to_iso_z,
    now_epoch,
    future_epoch,
)

# ============================================================
# CONSTANTES INTERNAS
# ============================================================

JWT_ALGORITHM = "HS256"

# ============================================================
# HELPERS PRIVADOS
# ============================================================

def _build_user_claim(user: Any) -> Dict[str, Any]:
    """
    Construye el objeto `user` que se incluye en el payload
    del access token.

    Este objeto existe EXCLUSIVAMENTE para facilitar al frontend:
    - identificación del usuario
    - carga de preferencias
    - lectura de permisos básicos

    Reglas:
    - Nunca incluir información sensible
    - Nunca incluir hashes o secretos
    - Nunca incluir objetos complejos o no serializables

    Args:
        user: instancia del modelo User.

    Returns:
        dict serializable con información mínima del usuario.
    """
    return {
        "id": user.id,
        "username": user.username,
        "rol": user.rol,
        "email": getattr(user, "email", None),
        "user_language": getattr(user, "user_language", None),
        "user_theme": getattr(user, "user_theme", None),
        "is_active": user.is_active,
        "last_login": dt_to_iso_z(getattr(user, "last_login", None)),
    }

# ============================================================
# CREACIÓN DE TOKENS
# ============================================================

def create_access_token(user: Any) -> str:
    """
    Crea un JWT de acceso (access token).

    Uso:
    - Se devuelve al frontend tras login
    - Se envía en cada request protegido (Authorization: Bearer)

    Payload estándar:
    - sub: user.id
    - username
    - rol
    - password_changed_at (normalizado)
    - user (objeto auxiliar para frontend)
    - type = "access"
    - iat / exp (epoch seconds)

    Args:
        user: instancia del modelo User.

    Returns:
        JWT access token firmado.
    """
    payload = {
        "sub": user.id,
        "username": user.username,
        "rol": user.rol,
        "password_changed_at": dt_to_iso_z(user.password_changed_at),
        "user": _build_user_claim(user),
        "type": "access",
        "iat": now_epoch(),
        "exp": future_epoch(
            timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
        ),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def create_refresh_token(user: Any) -> str:
    """
    Crea un JWT de refresco (refresh token).

    Uso:
    - Se devuelve junto con el access token en login
    - Se utiliza únicamente para obtener un nuevo access token
    - NO está pensado para ser leído por el frontend

    Payload:
    - sub
    - password_changed_at
    - type = "refresh"
    - iat / exp

    Args:
        user: instancia del modelo User.

    Returns:
        JWT refresh token firmado.
    """
    payload = {
        "sub": user.id,
        "password_changed_at": dt_to_iso_z(user.password_changed_at),
        "type": "refresh",
        "iat": now_epoch(),
        "exp": future_epoch(
            timedelta(days=settings.REFRESH_EXPIRE_DAYS)
        ),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

# ============================================================
# DECODIFICACIÓN
# ============================================================

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodifica un JWT y devuelve su payload.

    IMPORTANTE:
    - Esta función NO valida permisos
    - La validación funcional del token se hace en el middleware
    - Aquí solo se verifica firma y expiración

    Args:
        token: JWT en formato string.

    Returns:
        dict con el payload decodificado.

    Raises:
        jwt.ExpiredSignatureError
        jwt.InvalidTokenError
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )

# /src/app/security/jwt.py
