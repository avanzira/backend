# /src/app/controllers/products_controller.py
"""
ProductsController — v3.0

Controller de Products.

Responsabilidad:
- Exponer CRUD estándar heredado de BaseController
- Delegar la lógica en el ProductsService
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.products_service import products_service
from src.app.core.logging import get_logger

logger = get_logger(__name__)


class ProductsController(BaseController):
    """
    Controller de Products.
    """

    service = products_service


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
products_controller = ProductsController()

# /src/app/controllers/products_controller.py
