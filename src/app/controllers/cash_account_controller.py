# /src/app/controllers/cash_account_controller.py
"""
CashAccountController — v3.0

Controller de CashAccount.

Responsabilidad:
- Exponer CRUD estándar heredado de BaseController
- Delegar TODA la lógica de negocio y errores en el service

IMPORTANTE:
- No usa request
- No construye errores HTTP
- No controla manualmente estados inexistentes
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.cash_accounts_service import cash_accounts_service


class CashAccountController(BaseController):
    """
    Controller de CashAccount.
    """

    service = cash_accounts_service


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
cash_account_controller = CashAccountController()

# /src/app/controllers/cash_account_controller.py
