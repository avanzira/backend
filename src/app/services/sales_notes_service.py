# /src/app/services/sales_notes_service.py

"""
SalesNotesService — v3.0

Servicio de dominio para la gestión de SalesNote.

⚠️ NO ejecuta lógica de negocio de stock ni cash.
✅ Decide reglas documentales (DRAFT, líneas obligatorias).
⚠️ NO persiste movimientos.
⚠️ NO decide reglas contables.

Responsabilidades:
- CRUD de SalesNote en estado DRAFT
- Confirmar SalesNote:
  - orquestar movimientos de stock y cash
  - cambiar estado a CONFIRMED

Reglas de dominio:
- Solo las SalesNote en DRAFT son editables
- Las líneas se gestionan exclusivamente en sales_lines_service
- Los efectos se ejecutan exclusivamente en confirm()
"""

from flask import g

from src.app.services.base_service import BaseService
from src.app.services.stock_movements_service import stock_movements_service
from src.app.services.cash_movements_service import cash_movements_service

from src.app.models.sales_note import SalesNote
from src.app.models.sales_note_line import SalesNoteLine

from src.app.core import ( BadRequestException, ForbiddenException, NotFoundException, enum, db_session)
from datetime import datetime, timezone

class SalesNotesService(BaseService):
    """
    Servicio de dominio para SalesNote.
    """

    model = SalesNote

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_sale(self, sales_note_id: int) -> SalesNote:
        """
        Obtiene una SalesNote activa por ID o lanza excepción.
        """
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
        """
        Valida que la SalesNote esté en estado DRAFT.
        """
        if sale.status != enum.DocumentStatus.DRAFT:
            raise ForbiddenException(
                "SalesNote is not editable unless in DRAFT status"
            )

    def _get_lines(self, sales_note_id: int) -> list[SalesNoteLine]:
        """
        Obtiene las líneas activas asociadas a la SalesNote.
        """
        return (
            db_session.query(SalesNoteLine)
            .filter(
                SalesNoteLine.sales_note_id == sales_note_id,
                SalesNoteLine.is_active == True,
            )
            .all()
        )

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------
    def create(self, data: dict) -> SalesNote:
        """
        Crea una SalesNote en estado DRAFT.
        """
        data["status"] = enum.DocumentStatus.DRAFT
        data["total_amount"] = 0
        if "paid_amount" not in data:
            data["paid_amount"] = 0
        data["created_by"] = g.current_user.id if g.current_user else None
        return super().create(data)

    def update(self, sales_note_id: int, data: dict) -> SalesNote:
        """
        Actualiza una SalesNote solo si está en DRAFT.
        """
        sale = self._get_sale(sales_note_id)
        self._ensure_draft(sale)

        data["updated_by"] = g.current_user.id if g.current_user else None
        return super().update(sales_note_id, data)

    def delete(self, sales_note_id: int) -> bool:
        """
        Soft delete de una SalesNote solo si está en DRAFT.
        """
        sale = self._get_sale(sales_note_id)
        self._ensure_draft(sale)

        sale.is_active = False
        sale.deleted_at = datetime.now(timezone.utc)
        sale.updated_by = g.current_user.id if g.current_user else None
        db_session.commit()
        return 

    # ------------------------------------------------------------
    # MÉTODOS DE NEGOCIO
    # ------------------------------------------------------------
    def confirm(self, sales_note_id: int) -> SalesNote:
        """
        Confirma una SalesNote.

        NO decide reglas de negocio complejas ni valida invariantes de stock o cash; únicamente valida estado del documento y consistencia estructural.
        Su única responsabilidad es:

        - Reunir toda la información del documento
        - Lanzar los movimientos correspondientes
        - Si no hay errores, marcar el documento como CONFIRMED

        Todas las reglas de negocio (stock, cash, invariantes)
        se validan y ejecutan exclusivamente en los movement services.
        """
        sale = self._get_sale(sales_note_id)
        self._ensure_draft(sale)

        lines = self._get_lines(sale.id)
        if not lines:
            raise BadRequestException(
                "SalesNote cannot be confirmed without lines"
            )

        # --------------------------------------------------------
        # MOVIMIENTO DE STOCK
        #
        # Se lanza el movimiento de stock pasando TODA la información
        # necesaria (documento, líneas y fecha).
        # --------------------------------------------------------
        stock_movements_service.apply_movement(
            aggregate=sale,
            lines=lines,
            date=sale.date,
        )

        # --------------------------------------------------------
        # MOVIMIENTO DE CASH
        #
        # Se lanza el movimiento de cash con toda la información
        # del documento.
        # --------------------------------------------------------
        cash_movements_service.apply_movement(
            aggregate=sale,
            lines=lines,
            date=sale.date,
        )

        # --------------------------------------------------------
        # Cambio de estado del documento
        # --------------------------------------------------------
        sale.status = enum.DocumentStatus.CONFIRMED
        sale.updated_by = g.current_user.id if g.current_user else None

        db_session.commit()
        return sale


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
sales_notes_service = SalesNotesService()

# /src/app/services/sales_notes_service.py
