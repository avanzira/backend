# /src/app/services/stock_deposit_notes_service.py

"""
StockDepositNotesService — v3.0

Servicio de dominio para la gestión de StockDepositNotes.

⚠️ NO modifica stock directamente.
⚠️ NO crea ni actualiza StockProductLocation.
⚠️ NO persiste movimientos.

Responsabilidades:
- CRUD de StockDepositNotes en estado DRAFT
- Confirmar StockDepositNotes:
  - orquestar un único movimiento de stock
  - cambiar el estado a CONFIRMED

Reglas de dominio:
- El documento es editable solo en estado DRAFT
- El movimiento de stock se ejecuta exclusivamente en confirm()
- El signo del movimiento depende del documento que lo lanza
- El stock resultante nunca puede quedar negativo (invariante del movement)
"""

from flask import g

from src.app.services.base_service import BaseService
from src.app.services.stock_movements_service import stock_movements_service

from src.app.models.stock_deposit_note import StockDepositNote

from src.app.core import ( BadRequestException, ForbiddenException, NotFoundException, enum, db_session)
from datetime import datetime, timezone

class StockDepositNotesService(BaseService):
    """
    Servicio de dominio para StockDepositNotes.
    """

    model = StockDepositNote

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_note(self, note_id: int) -> StockDepositNote:
        """
        Obtiene una StockDepositNote activa por ID o lanza excepción.
        """
        note = (
            db_session.query(StockDepositNote)
            .filter(
                StockDepositNote.id == note_id,
                StockDepositNote.is_active == True,
            )
            .first()
        )
        if not note:
            raise NotFoundException("StockDepositNote not found")
        return note

    def _ensure_draft(self, note: StockDepositNote):
        """
        Valida que el documento esté en estado DRAFT.
        """
        if note.status != enum.DocumentStatus.DRAFT:
            raise ForbiddenException(
                "StockDepositNote is not editable unless in DRAFT status"
            )

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------
    def create(self, data: dict) -> StockDepositNote:
        """
        Crea una StockDepositNote en estado DRAFT.
        """
        data["status"] = enum.DocumentStatus.DRAFT
        data["created_by"] = g.current_user.id if g.current_user else None
        return super().create(data)

    def update(self, note_id: int, data: dict) -> StockDepositNote:
        """
        Actualiza una StockDepositNote solo si está en DRAFT.
        """
        note = self._get_note(note_id)
        self._ensure_draft(note)

        data["updated_by"] = g.current_user.id if g.current_user else None
        return super().update(note_id, data)

    def delete(self, note_id: int) -> bool:
        """
        Soft delete de una StockDepositNote solo si está en DRAFT.
        """
        note = self._get_note(note_id)
        self._ensure_draft(note)

        note.is_active = False
        note.deleted_at = datetime.now(timezone.utc)
        note.updated_by = g.current_user.id if g.current_user else None
        db_session.commit()
        return

    # ------------------------------------------------------------
    # MÉTODOS DE NEGOCIO
    # ------------------------------------------------------------
    def confirm(self, note_id: int) -> StockDepositNote:
        """
        Confirma una StockDepositNote.

        Este servicio NO decide reglas de negocio ni valida invariantes
        de stock. Su única responsabilidad es:

        - Reunir toda la información del documento
        - Lanzar el movimiento de stock correspondiente
        - Si no hay errores, marcar el documento como CONFIRMED

        Todas las reglas de negocio (signo del movimiento, validación
        de stock no negativo, etc.) se validan y ejecutan exclusivamente
        en el stock_movements_service.
        """
        note = self._get_note(note_id)
        self._ensure_draft(note)

        if note.quantity == 0:
            raise BadRequestException(
                "StockDepositNote quantity cannot be zero"
            )

        # --------------------------------------------------------
        # MOVIMIENTO DE STOCK
        #
        # Se lanza el movimiento de stock pasando TODA la información
        # necesaria (documento y fecha).
        #
        # El stock_movements_service:
        # - interpreta el documento
        # - determina el signo del movimiento
        # - valida invariantes (el stock resultante nunca queda negativo)
        # - aplica los cambios o lanza excepción
        # --------------------------------------------------------
        stock_movements_service.apply_movement(aggregate=note, lines=None, date=note.date)

        # --------------------------------------------------------
        # Cambio de estado del documento
        #
        # Si hemos llegado aquí, el movimiento se ha aplicado
        # correctamente (no hubo excepciones).
        # --------------------------------------------------------
        note.status = enum.DocumentStatus.CONFIRMED
        note.updated_by = g.current_user.id if g.current_user else None

        db_session.commit()
        return note


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
stock_deposit_notes_service = StockDepositNotesService()

# /src/app/services/stock_deposit_notes_service.py
