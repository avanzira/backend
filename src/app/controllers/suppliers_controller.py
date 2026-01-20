# /src/app/controllers/suppliers_controller.py
"""
SuppliersController — v3.0

Controller de Suppliers.

Responsabilidad:
- Exponer CRUD estándar heredado de BaseController
- Delegar la lógica en el SuppliersService
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.suppliers_service import suppliers_service
from src.app.core.logging import get_logger

logger = get_logger(__name__)


class SuppliersController(BaseController):
    """
    Controller de Suppliers.
    """

    service = suppliers_service


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
suppliers_controller = SuppliersController()

# /src/app/controllers/suppliers_controller.py
