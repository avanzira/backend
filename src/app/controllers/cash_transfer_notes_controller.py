# /src/app/controllers/cash_transfer_notes_controller.py
"""
CashTransferNotesController — v3.0

Responsabilidad (arquitectura v3.0):
- Exponer endpoints HTTP para CashTransferNotes.
- NO contiene lógica contable.
- NO modifica balances directamente.
- Delega todo en CashTransferNotesService.

Relación con Cash:
- El controller NO toca CashAccount.balance.
- Los efectos financieros se ejecutan solo en confirm().
- El movimiento real se ejecuta en cash_movements_service.

Flujo típico en la API:
1) Crear CashTransferNote (DRAFT)
   POST /api/cash_transfer_notes

2) Confirmar la transferencia
   POST /api/cash_transfer_notes/<id>/confirm
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.cash_transfer_notes_service import cash_transfer_notes_service


class CashTransferNotesController(BaseController):
    """
    Controller de CashTransferNotes.
    """

    service = cash_transfer_notes_service

    def confirm(self, id: int):
        """
        Confirma un documento de transferencia de efectivo.

        Efectos:
        - Lanza un movimiento de cash vía cash_movements_service
        - Cambia el estado del documento a CONFIRMED

        Nota:
        - Si el movimiento viola invariantes contables,
          se lanza excepción y el documento permanece en DRAFT.
        """
        note = self.service.confirm(id)
        return self.response_ok(note.to_dict())


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
cash_transfer_notes_controller = CashTransferNotesController()

# /src/app/controllers/cash_transfer_notes_controller.py
