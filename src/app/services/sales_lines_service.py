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

    def create_line(self, sales_note_id: int, data: dict):
        """
        Crea una línea asociada a una SalesNote.
        """
        if not sales_note_id:
            raise BadRequestException("sales_note_id is required")

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
        if sale.status != enum.DocumentStatus.DRAFT:
            raise ForbiddenException(
                "SalesNote is not editable unless in DRAFT status"
            )

        payload = dict(data)
        payload["sales_note_id"] = sales_note_id

        line = self.create(payload)

        sale.total_amount = sale.total_amount + line.total_price
        sale.paid_amount = sale.total_amount
        sale.updated_at = datetime.now(timezone.utc)
        sale.updated_by = g.current_user.id if g.current_user else None
        db_session.commit()

        return line


sales_lines_service = SalesLinesService()

# /src/app/services/sales_lines_service.py
