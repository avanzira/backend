# /src/app/services/sales_lines_service.py
"""
SalesLinesService — v3.0

Responsabilidad:
- Gestionar líneas de venta (SalesLine).
- Misma filosofía que PurchaseLinesService.
"""

from datetime import datetime, timezone
from flask import g

from src.app.services.base_service import BaseService
from src.app.core import (BadRequestException, ForbiddenException, NotFoundException, enum, db_session)
from src.app.models.sales_note import SalesNote
from src.app.models.sales_note_line import SalesNoteLine


class SalesLinesService(BaseService):
    model = SalesNoteLine

    def _get_sale(self, sales_note_id: int) -> SalesNote:
        sale = (
            db_session.query(SalesNote)
            .filter(
                SalesNote.id == sales_note_id,
                SalesNote.is_active == True,
            )
            .first()
        )
        if not sale:
            raise NotFoundException("SalesNote not found")
        return sale

    def _ensure_draft(self, sale: SalesNote):
        if sale.status != enum.DocumentStatus.DRAFT:
            raise ForbiddenException(
                "SalesNote is not editable unless in DRAFT status"
            )

    def _get_line(self, sales_note_id: int, line_id: int) -> SalesNoteLine:
        line = (
            db_session.query(SalesNoteLine)
            .filter(
                SalesNoteLine.id == line_id,
                SalesNoteLine.sales_note_id == sales_note_id,
                SalesNoteLine.is_active == True,
            )
            .first()
        )
        if not line:
            raise NotFoundException("SalesNoteLine not found")
        return line

    def _recalc_total(self, sale: SalesNote):
        lines = (
            db_session.query(SalesNoteLine)
            .filter(
                SalesNoteLine.sales_note_id == sale.id,
                SalesNoteLine.is_active == True,
            )
            .all()
        )
        total = sum((line.total_price for line in lines), 0)
        sale.total_amount = total
        sale.paid_amount = total
        sale.updated_at = datetime.now(timezone.utc)
        sale.updated_by = g.current_user.id if g.current_user else None

    def get_by_sales_note_id(self, sales_note_id: int) -> list[SalesNoteLine]:
        """
        Devuelve líneas activas asociadas a una SalesNote.
        """
        if not sales_note_id:
            raise BadRequestException("sales_note_id is required")

        return (
            db_session.query(SalesNoteLine)
            .filter(
                SalesNoteLine.sales_note_id == sales_note_id,
                SalesNoteLine.is_active == True,
            )
            .all()
        )

    def create_line(self, sales_note_id: int, data: dict):
        """
        Crea una línea asociada a una SalesNote.
        """
        if not sales_note_id:
            raise BadRequestException("sales_note_id is required")

        sale = self._get_sale(sales_note_id)
        self._ensure_draft(sale)

        payload = dict(data)
        payload["sales_note_id"] = sales_note_id

        line = self.create(payload)

        self._recalc_total(sale)
        db_session.commit()

        return line

    def update_line(self, sales_note_id: int, line_id: int, data: dict) -> SalesNoteLine:
        """
        Actualiza una línea asociada a una SalesNote.
        """
        if not sales_note_id:
            raise BadRequestException("sales_note_id is required")

        if "sales_note_id" in data:
            raise BadRequestException("sales_note_id is not editable")

        sale = self._get_sale(sales_note_id)
        self._ensure_draft(sale)

        line = self._get_line(sales_note_id, line_id)

        for key, value in data.items():
            if not hasattr(line, key):
                raise BadRequestException(f"Invalid field: {key}")
            setattr(line, key, value)

        line.updated_at = datetime.now(timezone.utc)
        line.updated_by = g.current_user.id if g.current_user else None

        self._recalc_total(sale)
        db_session.commit()
        return line

    def delete_line(self, sales_note_id: int, line_id: int):
        """
        Soft delete de una línea asociada a una SalesNote.
        """
        if not sales_note_id:
            raise BadRequestException("sales_note_id is required")

        sale = self._get_sale(sales_note_id)
        self._ensure_draft(sale)

        line = self._get_line(sales_note_id, line_id)
        line.is_active = False
        line.deleted_at = datetime.now(timezone.utc)
        line.updated_at = datetime.now(timezone.utc)
        line.updated_by = g.current_user.id if g.current_user else None

        self._recalc_total(sale)
        db_session.commit()
        return


sales_lines_service = SalesLinesService()

# /src/app/services/sales_lines_service.py
