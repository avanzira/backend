# /src/app/controllers/auth_controller.py
"""
AuthController — v3.0

Controller de autenticación.

Responsabilidades:
- Exponer endpoints NO CRUD relacionados con autenticación
- Validar input HTTP mínimo
- Delegar lógica de negocio al AuthService
- Serializar respuestas HTTP (JSON)

IMPORTANTE:
- NO contiene lógica de negocio
- NO accede directamente a base de datos
- Las excepciones se gestionan en core.exceptions.handlers
"""

from flask import request, g

from src.app.controllers.base_controller import BaseController
from src.app.services.auth_service import auth_service
from src.app.core.logging import get_logger
from src.app.core.exceptions.base import BadRequestException

logger = get_logger(__name__)


class AuthController(BaseController):
    """
    Controller de autenticación.

    Este controller expone endpoints especiales de auth
    que no siguen el patrón CRUD estándar.
    """

    service = auth_service

    # ------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------
    def login(self):
        """
        Autentica un usuario y devuelve tokens JWT.

        Endpoint:
            POST /api/auth/login

        Request JSON esperado:
            {
                "username": str,
                "password": str
            }

        Respuesta:
            200 OK
            {
                "access_token": str,
                "refresh_token": str,
                "user": dict
            }

        Raises:
            BadRequestException: Si el body no existe.
            UnauthorizedException: Si las credenciales son inválidas.
        """

        logger.info("Login request received")

        data = request.get_json()
        if not data:
            raise BadRequestException("Request body required")

        result = self.service.authenticate(
            data.get("username"),
            data.get("password"),
        )

        return self.response_ok(
            {
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "user": result["user"].to_dict(),
            }
        )

    # ------------------------------------------------------------
    # REFRESH TOKEN
    # ------------------------------------------------------------
    def refresh(self, token: str):
        """
        Refresca los tokens JWT a partir de un refresh_token válido.

        Endpoint:
            POST /api/auth/refresh

        Args:
            token (str): Refresh token JWT.

        Respuesta:
            200 OK
            {
                "access_token": str,
                "refresh_token": str,
                "user": dict
            }

        Raises:
            UnauthorizedException: Si el token es inválido o ha expirado.
        """

        logger.info("Refreshing token")

        result = self.service.refresh_token(token)

        return self.response_ok(
            {
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "user": result["user"].to_dict(),
            }
        )

    # ------------------------------------------------------------
    # ME
    # ------------------------------------------------------------
    def me(self):
        """
        Devuelve la información del usuario autenticado.

        Endpoint:
            GET /api/auth/me

        Requisitos:
            - JWT válido en el contexto (middleware)

        Respuesta:
            200 OK
            {
                ... user serializado ...
            }
        """

        logger.info("Fetching authenticated user data")
        return self.response_ok(g.current_user.to_dict())


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
auth_controller = AuthController()
# /src/app/controllers/auth_controller.py
