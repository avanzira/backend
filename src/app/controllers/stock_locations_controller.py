# /src/app/controllers/stock_locations_controller.py
"""
StockLocationsController — v3.0

Controller de StockLocations.

Responsabilidad:
- Exponer CRUD estándar heredado de BaseController
- Delegar TODA la lógica de negocio y errores en el service

IMPORTANTE:
- No usa request
- No construye errores HTTP
- No controla manualmente estados inexistentes
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.stock_locations_service import stock_locations_service


class StockLocationsController(BaseController):
    """
    Controller de StockLocations.
    """

    service = stock_locations_service


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
stock_locations_controller = StockLocationsController()

# /src/app/controllers/stock_locations_controller.py
