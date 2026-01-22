# /src/app/controllers/sales_notes_controller.py
"""
SalesNotesController — v3.0

Responsabilidad:
- Orquestar el flujo de confirmación de una venta.
- Mantiene la misma semántica que PurchaseNotesController.

Diferencias clave con Purchase:
- No genera deuda (paid_amount suele ser igual a total_amount).
- Impacta stock en salida.
"""

from src.app.controllers.base_controller import BaseController
from src.app.services.sales_notes_service import sales_notes_service
from datetime import date as py_date


class SalesNotesController(BaseController):
    service = sales_notes_service

    def create(self):
        """
        Crea una SalesNote en estado DRAFT.
        """
        payload = self.parse_json(required=True)

        # ---------------------------------------------------------
        # NORMALIZAR DATE (API → dominio)
        # ---------------------------------------------------------
        if "date" in payload and isinstance(payload["date"], str):
            payload["date"] = py_date.fromisoformat(payload["date"])

        note = self.service.create(payload)
        return self.response_created(note.to_dict())

    def update(self, id: int):
        """
        Actualiza una SalesNote en estado DRAFT.
        """
        payload = self.parse_json(required=True)

        if "date" in payload and isinstance(payload["date"], str):
            payload["date"] = py_date.fromisoformat(payload["date"])

        note = self.service.update(id, payload)
        return self.response_ok(note.to_dict())

    def confirm(self, id: int):
        """
        Confirma una SalesNote existente.
        """
        note = self.service.confirm(id)
        return self.response_ok(note.to_dict())


sales_notes_controller = SalesNotesController()

# /src/app/controllers/sales_notes_controller.py
