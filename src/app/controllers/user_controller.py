# /src/app/controllers/user_controller.py
"""
UserController — v3.0

Controller de usuarios.

Responsabilidad:
- Exponer CRUD estándar heredado de BaseController
- Exponer endpoint explícito de cambio de contraseña
- Delegar TODA la lógica de seguridad en el service y core

IMPORTANTE:
- No usa request directamente
- No construye errores HTTP
- No devuelve mensajes arbitrarios
"""

from flask import g
from src.app.controllers.base_controller import BaseController
from src.app.services.users_service import users_service


class UserController(BaseController):
    """
    Controller de usuarios.
    """

    service = users_service

    # ------------------------------------------------------------
    # ENDPOINTS ESPECÍFICOS
    # ------------------------------------------------------------
    def change_password(self):
        """
        Cambia la contraseña del usuario autenticado.
        """
        data = self.parse_json(required=True)

        user_id = g.current_user.id
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        self.service.change_password(
            user_id=user_id,
            old_password=old_password,
            new_password=new_password,
        )

        return self.response_ok({})


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
user_controller = UserController()

# /src/app/controllers/user_controller.py
