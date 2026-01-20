# /src/app/api/routers/cash_transfer_notes_router.py
"""
cash_transfer_notes router — v3.0

Router del documento CashTransferNotes.

Responsabilidad:
- Exponer CRUD estándar
- Exponer endpoint explícito de confirmación

IMPORTANTE:
- No contiene lógica de negocio
- No importa request
- Delegación total en el controller
"""

from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.cash_transfer_notes_controller import (
    cash_transfer_notes_controller,
)

# ------------------------------------------------------------
# ROUTER CRUD BASE
# ------------------------------------------------------------
cash_transfer_notes_router = BaseRouter(
    "cash_transfer_notes",
    cash_transfer_notes_controller,
).router


# ------------------------------------------------------------
# ENDPOINTS EXPLÍCITOS DE DOCUMENTO
# ------------------------------------------------------------
@cash_transfer_notes_router.post("/<int:id>/confirm")
def confirm(id: int):
    """
    Confirma un CashTransferNotes.
    """
    return cash_transfer_notes_controller.confirm(id)

# /src/app/api/routers/cash_transfer_notes_router.py
