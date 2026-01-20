# /src/app/security/middleware.py
"""
JWT Middleware — v3.0

Middleware de seguridad para Flask encargado de validar tokens JWT
en todas las rutas protegidas del backend DemeArizOil.

Responsabilidades principales:
- Extraer el token JWT del header Authorization
- Validar firma y expiración
- Verificar tipo de token (solo access)
- Cargar el usuario desde base de datos
- Verificar estado activo del usuario
- Invalidar tokens tras cambio de contraseña
- Inyectar información de seguridad y auditoría en el contexto global (g)

IMPORTANTE:
- Este middleware NO contiene lógica de negocio.
- Este middleware NO genera tokens.
- Este middleware NO maneja respuestas HTTP directamente:
  lanza excepciones que son manejadas por core.exceptions.handlers.

Referencia normativa:
- security_v3.0.md
"""

from __future__ import annotations

import jwt
from flask import g, request

from src.app.core.config.database import db_session
from src.app.core.config.settings import settings
from src.app.core.exceptions.base import UnauthorizedException
from src.app.core.utils.datetime_utils import dt_to_iso_z
from src.app.models.user import User

# ============================================================
# REGISTRO DEL MIDDLEWARE
# ============================================================

def jwt_middleware(app) -> None:
    """
    Registra el middleware JWT en la aplicación Flask.

    Se engancha mediante `before_request` y se ejecuta
    automáticamente antes de cada request HTTP.

    Args:
        app: instancia de la aplicación Flask.
    """

    # ------------------------------------------------------------
    # BEFORE REQUEST
    # ------------------------------------------------------------
    @app.before_request
    def validate_jwt():
        """
        Valida el token JWT de acceso para todas las rutas protegidas.

        Flujo de validación (orden crítico):
        1. Comprobar si la ruta es pública
        2. Extraer header Authorization
        3. Validar formato Bearer <token>
        4. Decodificar JWT (firma + expiración)
        5. Verificar tipo de token (access)
        6. Extraer user_id (sub)
        7. Cargar usuario desde base de datos
        8. Verificar usuario activo
        9. Comparar password_changed_at (invalidación automática)
        10. Inyectar usuario y datos de auditoría en `g`

        Si cualquiera de los pasos falla:
        - Se lanza UnauthorizedException
        - La respuesta HTTP la construye el handler global
        """

        # --------------------------------------------------------
        # 1. RUTAS PÚBLICAS
        # --------------------------------------------------------
        # Las rutas públicas se definen de forma centralizada en settings
        if request.path in settings.PUBLIC_PATHS:
            return None

        # --------------------------------------------------------
        # 2. HEADER AUTHORIZATION
        # --------------------------------------------------------
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise UnauthorizedException("Missing Authorization header")

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise UnauthorizedException("Invalid Authorization scheme")
        except ValueError:
            raise UnauthorizedException("Invalid Authorization header format")

        # --------------------------------------------------------
        # 3. DECODIFICACIÓN DEL TOKEN
        # --------------------------------------------------------
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Invalid token")

        # --------------------------------------------------------
        # 4. TIPO DE TOKEN
        # --------------------------------------------------------
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type")

        # --------------------------------------------------------
        # 5. IDENTIDAD DEL USUARIO
        # --------------------------------------------------------
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token (missing sub)")

        token_pwd_changed = payload.get("password_changed_at")
        if not token_pwd_changed:
            raise UnauthorizedException("Invalid token (missing password_changed_at)")

        # --------------------------------------------------------
        # 6. CARGA DEL USUARIO DESDE BD
        # --------------------------------------------------------
        user = (
            db_session.query(User)
            .filter_by(id=user_id, is_active=True)
            .first()
        )

        if not user:
            raise UnauthorizedException("User not found or inactive")

        # --------------------------------------------------------
        # 7. INVALIDACIÓN POR CAMBIO DE CONTRASEÑA
        # --------------------------------------------------------
        # La comparación se hace SIEMPRE usando la normalización canónica
        # definida en datetime_utils.py
        current_pwd_changed = dt_to_iso_z(user.password_changed_at)

        if token_pwd_changed != current_pwd_changed:
            raise UnauthorizedException("Token invalidated (password changed)")

        # --------------------------------------------------------
        # 8. INYECCIÓN DE CONTEXTO GLOBAL
        # --------------------------------------------------------
        # Usuario autenticado disponible durante todo el request
        g.current_user = user

        # Datos de auditoría (no persistencia aquí)
        g.audit_user_id = user.id
        g.audit_ip = (
            request.headers.get("X-Forwarded-For")
            or request.remote_addr
            or "unknown"
        )
        g.audit_user_agent = request.headers.get("User-Agent", "unknown")

        return None

# /src/app/security/middleware.py
