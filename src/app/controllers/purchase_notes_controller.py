# /src/app/controllers/purchase_notes_controller.py
"""
PurchaseNotesController — v3.0

Responsabilidad (arquitectura v3.0):
- Orquestar flujos de negocio de alto nivel para PurchaseNote.
- NO contiene lógica de dominio (cálculos, invariantes).
- NO persiste relaciones complejas directamente.
- Coordina services especializados.

Flujo expuesto por la API:
- POST /api/purchase_notes
    Crea una PurchaseNote en estado DRAFT (sin líneas).
- POST /api/purchase_notes/<id>/confirm
    Confirma una PurchaseNote existente (movimientos + estado CONFIRMED)

IMPORTANTE:
- Las líneas NO son un campo del modelo PurchaseNote.
- Las líneas se gestionan vía el endpoint de líneas.
"""

from src.app.controllers.base_controller import BaseController
from src.app.core import BadRequestException
from src.app.services.purchase_notes_service import purchase_notes_service

from datetime import date as py_date


class PurchaseNotesController(BaseController):
    """
    Controller de PurchaseNote.
    """
    service = purchase_notes_service

    def create(self):
        """
        Crea una PurchaseNote en estado DRAFT.
        """
        payload = self.parse_json(required=True)

        # ---------------------------------------------------------
        # NORMALIZAR DATE (API → dominio)
        # ---------------------------------------------------------
        if "date" in payload and isinstance(payload["date"], str):
            payload["date"] = py_date.fromisoformat(payload["date"])

        # ---------------------------------------------------------
        # VALIDACIÓN DRAFT: no se permite paid_amount > 0 sin líneas
        # ---------------------------------------------------------
        paid_amount = payload.get("paid_amount")
        if paid_amount is not None and float(paid_amount) > 0:
            raise BadRequestException("paid_amount must be 0 when creating a DRAFT purchase note")

        note = self.service.create(payload)
        return self.response_created(note.to_dict())

    def update(self, id: int):
        """
        Actualiza una PurchaseNote en estado DRAFT.
        """
        payload = self.parse_json(required=True)

        if "date" in payload and isinstance(payload["date"], str):
            payload["date"] = py_date.fromisoformat(payload["date"])

        note = self.service.update(id, payload)
        return self.response_ok(note.to_dict())

    def confirm(self, id: int):
        """
        Confirma una PurchaseNote existente.
        """
        note = self.service.confirm(id)
        return self.response_ok(note.to_dict())


purchase_notes_controller = PurchaseNotesController()

# /src/app/controllers/purchase_notes_controller.py
