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

    def _get_purchase(self, purchase_note_id: int) -> PurchaseNote:
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
        return purchase

    def _ensure_draft(self, purchase: PurchaseNote):
        if purchase.status != enum.DocumentStatus.DRAFT:
            raise ForbiddenException(
                "PurchaseNote is not editable unless in DRAFT status"
            )

    def _get_line(self, purchase_note_id: int, line_id: int) -> PurchaseNoteLine:
        line = (
            db_session.query(PurchaseNoteLine)
            .filter(
                PurchaseNoteLine.id == line_id,
                PurchaseNoteLine.purchase_note_id == purchase_note_id,
                PurchaseNoteLine.is_active == True,
            )
            .first()
        )
        if not line:
            raise NotFoundException("PurchaseNoteLine not found")
        return line

    def _recalc_total(self, purchase: PurchaseNote):
        lines = (
            db_session.query(PurchaseNoteLine)
            .filter(
                PurchaseNoteLine.purchase_note_id == purchase.id,
                PurchaseNoteLine.is_active == True,
            )
            .all()
        )
        total = sum((line.total_price for line in lines), 0)
        if purchase.paid_amount > total:
            raise BadRequestException("paid_amount cannot exceed total_amount")
        purchase.total_amount = total
        purchase.updated_at = datetime.now(timezone.utc)
        purchase.updated_by = g.current_user.id if g.current_user else None

    def get_by_purchase_note_id(self, purchase_note_id: int) -> list[PurchaseNoteLine]:
        """
        Devuelve líneas activas asociadas a una PurchaseNote.
        """
        if not purchase_note_id:
            raise BadRequestException("purchase_note_id is required")

        return (
            db_session.query(PurchaseNoteLine)
            .filter(
                PurchaseNoteLine.purchase_note_id == purchase_note_id,
                PurchaseNoteLine.is_active == True,
            )
            .all()
        )

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

        purchase = self._get_purchase(purchase_note_id)
        self._ensure_draft(purchase)

        payload = dict(data)
        payload["purchase_note_id"] = purchase_note_id

        line = self.create(payload)

        self._recalc_total(purchase)
        db_session.commit()

        return line

    def update_line(self, purchase_note_id: int, line_id: int, data: dict) -> PurchaseNoteLine:
        """
        Actualiza una línea asociada a una PurchaseNote.
        """
        if not purchase_note_id:
            raise BadRequestException("purchase_note_id is required")

        if "purchase_note_id" in data:
            raise BadRequestException("purchase_note_id is not editable")

        purchase = self._get_purchase(purchase_note_id)
        self._ensure_draft(purchase)

        line = self._get_line(purchase_note_id, line_id)

        for key, value in data.items():
            if not hasattr(line, key):
                raise BadRequestException(f"Invalid field: {key}")
            setattr(line, key, value)

        line.updated_at = datetime.now(timezone.utc)
        line.updated_by = g.current_user.id if g.current_user else None

        self._recalc_total(purchase)
        db_session.commit()
        return line

    def delete_line(self, purchase_note_id: int, line_id: int):
        """
        Soft delete de una línea asociada a una PurchaseNote.
        """
        if not purchase_note_id:
            raise BadRequestException("purchase_note_id is required")

        purchase = self._get_purchase(purchase_note_id)
        self._ensure_draft(purchase)

        line = self._get_line(purchase_note_id, line_id)
        line.is_active = False
        line.deleted_at = datetime.now(timezone.utc)
        line.updated_at = datetime.now(timezone.utc)
        line.updated_by = g.current_user.id if g.current_user else None

        self._recalc_total(purchase)
        db_session.commit()
        return


purchase_lines_service = PurchaseLinesService()

# /src/app/services/purchase_lines_service.py
