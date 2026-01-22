# /src/app/controllers/stock_deposit_notes_controller.py
"""
StockDepositNotesController — v3.0

Responsabilidad (arquitectura v3.0):
- Exponer endpoints HTTP para StockDepositNotes.
- NO contiene lógica de negocio.
- NO modifica stock.
- Delega completamente en StockDepositNotesService.

Relación con Stock:
- El controller NO crea ni modifica StockProductLocation.
- El stock se modifica únicamente en confirm().
- El movimiento real se ejecuta en stock_movements_service.

Flujo típico en la API:
1) Crear StockDepositNote (DRAFT)
   POST /api/stock_deposit_notes

2) Confirmar el depósito
   POST /api/stock_deposit_notes/<id>/confirm
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.stock_deposit_notes_service import stock_deposit_notes_service
from datetime import date as py_date


class StockDepositNotesController(BaseController):
    """
    Controller de StockDepositNotes.
    """

    service = stock_deposit_notes_service

    def create(self):
        """
        Crea un StockDepositNote en estado DRAFT.
        """
        payload = self.parse_json(required=True)

        if "date" in payload and isinstance(payload["date"], str):
            payload["date"] = py_date.fromisoformat(payload["date"])

        note = self.service.create(payload)
        return self.response_created(note.to_dict())

    def update(self, id: int):
        """
        Actualiza un StockDepositNote en estado DRAFT.
        """
        payload = self.parse_json(required=True)

        if "date" in payload and isinstance(payload["date"], str):
            payload["date"] = py_date.fromisoformat(payload["date"])

        note = self.service.update(id, payload)
        return self.response_ok(note.to_dict())

    def confirm(self, id: int):
        """
        Confirma un documento de depósito de stock.

        Efectos:
        - Lanza un movimiento de stock vía stock_movements_service
        - Cambia el estado del documento a CONFIRMED

        Nota:
        - Si el movimiento viola invariantes (ej. stock negativo),
          se lanza excepción y el documento permanece en DRAFT.
        """
        note = self.service.confirm(id)
        return self.response_ok(note.to_dict())


# ------------------------------------------------------------
# INSTANCIA EXPORTADA
# ------------------------------------------------------------
stock_deposit_notes_controller = StockDepositNotesController()

# /src/app/controllers/stock_deposit_notes_controller.py
