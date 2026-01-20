# /src/app/controllers/customers_controller.py
"""
CustomersController — v3.0

Controller de Customers.

Responsabilidad:
- Exponer CRUD estándar heredado de BaseController
- Delegar TODA la lógica de negocio en el service

IMPORTANTE:
- No redefine métodos CRUD
- No usa request
- No construye errores HTTP
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.customers_service import customers_service


class CustomersController(BaseController):
    """
    Controller de Customers.
    """

    service = customers_service


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
customers_controller = CustomersController()

# /src/app/controllers/customers_controller.py
