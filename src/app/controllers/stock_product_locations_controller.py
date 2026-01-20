# /src/app/controllers/stock_product_locations_controller.py
"""
StockProductLocationsController — v3.0

Controller de StockProductLocations.

Responsabilidad:
- Exponer CRUD estándar heredado de BaseController
- Delegar la lógica en el StockProductLocationsService
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.stock_product_locations_service import stock_product_locations_service
from src.app.core.logging import get_logger

logger = get_logger(__name__)


class StockProductLocationsController(BaseController):
    """
    Controller de StockProductLocations.
    """

    service = stock_product_locations_service


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
stock_product_locations_controller = StockProductLocationsController()

# /src/app/controllers/stock_product_locations_controller.py
