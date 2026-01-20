# /src/app/controllers/_controller_extension_template.py
"""
<ControllerName>Controller — v3.0

Controller de dominio del sistema DemeArizOil.

Extiende BaseController para:
- Exponer CRUD estándar
- Añadir endpoints específicos de negocio

IMPORTANTE:
- Importa una INSTANCIA del service
- Exporta una INSTANCIA del controller
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.service_name_service import service_name_service
from src.app.core.exceptions import BadRequestException


class ControllerNameController(BaseController):
    """
    Controller para <Entidad / Documento>.

    Hereda CRUD de BaseController.
    """

    service = service_name_service

    # ------------------------------------------------------------
    # ENDPOINTS ESPECÍFICOS DE NEGOCIO
    # ------------------------------------------------------------
    def special_action(self):
        """
        Endpoint de negocio específico.
        """
        data = self.parse_json(required=True)

        if "required_field" not in data:
            raise BadRequestException("required_field is mandatory")

        result = self.service.special_method(data)
        return self.response_ok(result)


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
controller_name_controller = ControllerNameController()

# /src/app/controllers/_controller_extension_template.py
