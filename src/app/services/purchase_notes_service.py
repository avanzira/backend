# /src/app/services/purchase_notes_service.py

"""
PurchaseNotesService — v3.0

Servicio de dominio para la gestión de PurchaseNote.

⚠️ NO ejecuta lógica de negocio de stock ni cash.
✅ Decide reglas documentales (DRAFT, líneas obligatorias).
⚠️ NO persiste movimientos.
⚠️ NO decide reglas contables.

Responsabilidades:
- CRUD de PurchaseNote en estado DRAFT
- Confirmar PurchaseNote:
  - orquestar movimientos de stock y cash
  - cambiar estado a CONFIRMED

Reglas de dominio:
- Solo las PurchaseNote en DRAFT son editables
- Las líneas se gestionan exclusivamente en purchase_lines_service
- Los efectos se ejecutan exclusivamente en confirm()
"""

from flask import g

from src.app.services.base_service import BaseService
from src.app.services.stock_movements_service import stock_movements_service
from src.app.services.cash_movements_service import cash_movements_service

from src.app.models.purchase_note import PurchaseNote
from src.app.models.purchase_note_line import PurchaseNoteLine

from src.app.core import (BadRequestException, ForbiddenException, NotFoundException, enum, db_session)
from datetime import datetime, timezone


class PurchaseNotesService(BaseService):
    """
    Servicio de dominio para PurchaseNote.
    """

    model = PurchaseNote

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_purchase(self, purchase_note_id: int) -> PurchaseNote:
        """
        Obtiene una PurchaseNote activa por ID o lanza excepción.
        """
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
        """
        Valida que la PurchaseNote esté en estado DRAFT.
        """
        if purchase.status != enum.DocumentStatus.DRAFT:
            raise ForbiddenException(
                "PurchaseNote is not editable unless in DRAFT status"
            )

    def _get_lines(self, purchase_note_id: int) -> list[PurchaseNoteLine]:
        """
        Obtiene las líneas activas asociadas a la PurchaseNote.
        """
        return (
            db_session.query(PurchaseNoteLine)
            .filter(
                PurchaseNoteLine.purchase_note_id == purchase_note_id,
                PurchaseNoteLine.is_active == True,
            )
            .all()
        )

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------
    def create(self, data: dict) -> PurchaseNote:
        """
        Crea una PurchaseNote en estado DRAFT.
        """
        data["status"] = enum.DocumentStatus.DRAFT
        data["total_amount"] = 0
        if "paid_amount" not in data:
            data["paid_amount"] = 0
        data["created_by"] = g.current_user.id if g.current_user else None
        return super().create(data)

    def update(self, purchase_note_id: int, data: dict) -> PurchaseNote:
        """
        Actualiza una PurchaseNote solo si está en DRAFT.
        """
        purchase = self._get_purchase(purchase_note_id)
        self._ensure_draft(purchase)

        data["updated_by"] = g.current_user.id if g.current_user else None
        return super().update(purchase_note_id, data)

    def delete(self, purchase_note_id: int) -> bool:
        """
        Soft delete de una PurchaseNote solo si está en DRAFT.
        """
        purchase = self._get_purchase(purchase_note_id)
        self._ensure_draft(purchase)

        purchase.is_active = False
        purchase.deleted_at = datetime.now(timezone.utc)

        purchase.updated_by = g.current_user.id if g.current_user else None
        db_session.commit()
        return

    # ------------------------------------------------------------
    # MÉTODOS DE NEGOCIO
    # ------------------------------------------------------------
    def confirm(self, purchase_note_id: int) -> PurchaseNote:
        """
        Confirma una PurchaseNote.

        NO decide reglas de negocio complejas ni valida invariantes de stock o cash; únicamente valida estado del documento y consistencia estructural.
        Su única responsabilidad es:

        - Reunir toda la información del documento
        - Lanzar los movimientos correspondientes
        - Si no hay errores, marcar el documento como CONFIRMED

        Todas las reglas de negocio (stock, cash, deuda, invariantes)
        se validan y ejecutan exclusivamente en los movement services.
        """
        purchase = self._get_purchase(purchase_note_id)
        self._ensure_draft(purchase)

        lines = self._get_lines(purchase.id)
        if not lines:
            raise BadRequestException(
                "PurchaseNote cannot be confirmed without lines"
            )

        total = sum((line.total_price for line in lines), 0)
        if purchase.paid_amount > total:
            raise BadRequestException("paid_amount cannot exceed total_amount")
        purchase.total_amount = total

        # --------------------------------------------------------
        # MOVIMIENTO DE STOCK
        #
        # Se lanza el movimiento de stock pasando TODA la información
        # necesaria (documento, líneas y fecha).
        # --------------------------------------------------------
        stock_movements_service.apply_movement(
            aggregate=purchase,
            lines=lines,
            date=purchase.date,
        )

        # --------------------------------------------------------
        # MOVIMIENTO DE CASH
        #
        # Se lanza el movimiento de cash con toda la información
        # del documento.
        # --------------------------------------------------------
        cash_movements_service.apply_movement(
            aggregate=purchase,
            lines=lines,
            date=purchase.date,
        )

        # --------------------------------------------------------
        # Cambio de estado del documento
        # --------------------------------------------------------
        purchase.status = enum.DocumentStatus.CONFIRMED
        purchase.updated_at = datetime.now(timezone.utc)
        purchase.updated_by = g.current_user.id if g.current_user else None

        db_session.commit()
        return purchase


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
purchase_notes_service = PurchaseNotesService()

# /src/app/services/purchase_notes_service.py
