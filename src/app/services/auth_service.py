# /src/app/services/auth_service.py
"""
AuthService — v3.0

Servicio de autenticación del sistema.

Responsabilidades:
- Verificar credenciales de usuario
- Emitir tokens JWT (access / refresh)
- Refrescar tokens a partir de refresh_token

Reglas de arquitectura:
- NO serializa usuarios
- NO construye payloads HTTP
- Devuelve User ORM + tokens
- Toda la lógica de negocio de auth vive aquí
"""

from src.app.core.config.database import db_session
from src.app.core.exceptions.base import UnauthorizedException
from src.app.models.user import User
from src.app.security.password import verify_password
from src.app.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.app.core.utils.datetime_utils import dt_to_iso_z


class AuthService:
    """
    Servicio de autenticación.

    Este service encapsula toda la lógica de negocio relacionada
    con autenticación y gestión de tokens.
    """

    # ------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------
    def authenticate(self, username: str, password: str) -> dict:
        """
        Autentica un usuario a partir de credenciales.

        Flujo:
        - Busca el usuario activo por username
        - Verifica la contraseña
        - Emite access_token y refresh_token

        Args:
            username (str): Nombre de usuario.
            password (str): Contraseña en texto plano.

        Raises:
            UnauthorizedException: Si las credenciales son inválidas.

        Returns:
            dict:
                {
                    "access_token": str,
                    "refresh_token": str,
                    "user": User
                }
        """

        user = (
            db_session.query(User)
            .filter(User.username == username, User.is_active == True)
            .first()
        )

        if not user:
            raise UnauthorizedException("Invalid credentials")

        if not verify_password(password, user.hash_password):
            raise UnauthorizedException("Invalid credentials")

        return {
            "access_token": create_access_token(user),
            "refresh_token": create_refresh_token(user),
            "user": user,
        }

    # ------------------------------------------------------------
    # REFRESH TOKEN
    # ------------------------------------------------------------
    def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresca los tokens JWT a partir de un refresh_token válido.

        Validaciones realizadas:
        - El token es de tipo "refresh"
        - El token contiene un subject (user_id)
        - El usuario existe y está activo
        - El token no ha sido invalidado por cambio de contraseña

        Args:
            refresh_token (str): Token JWT de tipo refresh.

        Raises:
            UnauthorizedException: Si el token es inválido o ha sido invalidado.

        Returns:
            dict:
                {
                    "access_token": str,
                    "refresh_token": str,
                    "user": User
                }
        """

        payload = decode_token(refresh_token)

        # Validación de tipo de token
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")

        user = (
            db_session.query(User)
            .filter(User.id == user_id, User.is_active == True)
            .first()
        )

        if not user:
            raise UnauthorizedException("Invalid refresh token")

        # Invalida tokens antiguos si se cambió la contraseña
        if payload.get("password_changed_at") != dt_to_iso_z(
            user.password_changed_at
        ):
            raise UnauthorizedException("Token no longer valid")

        return {
            "access_token": create_access_token(user),
            "refresh_token": create_refresh_token(user),
            "user": user,
        }


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
auth_service = AuthService()
# /src/app/services/auth_service.py
