# /src/app/controllers/_special_controller_template.py
"""
<ControllerName>Controller — v3.0

Controller especial del sistema DemeArizOil.

Responsabilidad:
- Exponer endpoints NO CRUD
- Delegar en services especiales

IMPORTANTE:
- NO expone CRUD
- Importa una INSTANCIA del service especial
- Exporta una INSTANCIA del controller
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.special_service_name_service import special_service_name_service
from src.app.core.exceptions import BadRequestException


class ControllerNameController(BaseController):
    """
    Controller especial.
    """

    service = special_service_name_service

    # ------------------------------------------------------------
    # ENDPOINTS ESPECIALES
    # ------------------------------------------------------------
    def action(self):
        """
        Ejecuta una acción especial del sistema.
        """
        data = self.parse_json(required=True)

        result = self.service.public_method(data)
        return self.response_ok(result)


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
controller_name_controller = ControllerNameController()

# /src/app/controllers/_special_controller_template.py
