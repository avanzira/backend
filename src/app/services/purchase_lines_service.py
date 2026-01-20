# /src/app/services/purchase_lines_service.py
"""
PurchaseLinesService — v3.0

Responsabilidad:
- Gestionar líneas de compra (PurchaseLine).
- Validar que la PurchaseNote exista y esté en DRAFT.
- NO confirma documentos.
- NO ejecuta movimientos.

Contrato:
- Las líneas siempre pertenecen a una PurchaseNote.
- El ID de la nota NO viene del modelo, se inyecta aquí.
"""

from datetime import datetime, timezone
from flask import g

from src.app.services.base_service import BaseService
from src.app.core import (BadRequestException, ForbiddenException, NotFoundException, enum, db_session)
from src.app.models.purchase_note import PurchaseNote
from src.app.models.purchase_note_line import PurchaseNoteLine


class PurchaseLinesService(BaseService):
    model = PurchaseNoteLine

    def create_line(self, purchase_note_id: int, data: dict):
        """
        Crea una línea asociada a una PurchaseNote.

        Parámetros:
        - purchase_note_id: ID de la nota (path param en la API)
        - data: payload de la línea SIN purchase_note_id

        Ejemplo de data:
        {
            "product_id": 1,
            "quantity": 10,
            "unit_price": 100,
            "total_price": 1000
        }
        """
        if not purchase_note_id:
            raise BadRequestException("purchase_note_id is required")

        purchase = (
            db_session.query(PurchaseNote)
            .filter(
                PurchaseNote.id == purchase_note_id,
                PurchaseNote.is_active == True,
            )
            .first()
        )
        if not purchase:
            raise NotFoundException("PurchaseNote not found")
        if purchase.status != enum.DocumentStatus.DRAFT:
            raise ForbiddenException(
                "PurchaseNote is not editable unless in DRAFT status"
            )

        payload = dict(data)
        payload["purchase_note_id"] = purchase_note_id

        line = self.create(payload)

        purchase.total_amount = purchase.total_amount + line.total_price
        purchase.updated_at = datetime.now(timezone.utc)
        purchase.updated_by = g.current_user.id if g.current_user else None
        db_session.commit()

        return line


purchase_lines_service = PurchaseLinesService()

# /src/app/services/purchase_lines_service.py
