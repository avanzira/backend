# /src/app/services/cash_transfer_notes_service.py

"""
CashTransferNotesService — v3.0

Servicio de dominio para la gestión de CashTransferNotes.

⚠️ NO modifica balances directamente.
⚠️ NO persiste movimientos.
⚠️ NO valida invariantes de cuentas.

Responsabilidades:
- CRUD de CashTransferNotes en estado DRAFT
- Confirmar CashTransferNotes:
  - orquestar un movimiento de efectivo
  - cambiar estado a CONFIRMED

Reglas de dominio:
- Solo los documentos en DRAFT son editables
- Los efectos se ejecutan exclusivamente en confirm()
- El movimiento usa la fecha del note
"""

from flask import g

from src.app.services.base_service import BaseService
from src.app.services.cash_movements_service import cash_movements_service

from src.app.models.cash_transfer_note import CashTransferNote

from src.app.core import (BadRequestException, ForbiddenException,  NotFoundException, enum, db_session)
from datetime import datetime, timezone

class CashTransferNotesService(BaseService):
    """
    Servicio de dominio para CashTransferNotes.
    """

    model = CashTransferNote

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_note(self, id: int) -> CashTransferNote:
        """
        Obtiene una CashTransferNotes activa por ID o lanza excepción.
        """
        note = (
            db_session.query(CashTransferNote)
            .filter(
                CashTransferNote.id == id,
                CashTransferNote.is_active == True,
            )
            .first()
        )
        if not note:
            raise NotFoundException("CashTransferNote not found")
        return note

    def _ensure_draft(self, note: CashTransferNote):
        """
        Valida que el documento esté en estado DRAFT.
        """
        if note.status != enum.DocumentStatus.DRAFT:
            raise ForbiddenException(
                "CashTransferNote is not editable unless in DRAFT status"
            )

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------
    def create(self, data: dict) -> CashTransferNote:
        """
        Crea una CashTransferNote en estado DRAFT.
        """
        data["status"] = enum.DocumentStatus.DRAFT
        data["created_by"] = g.current_user.id if g.current_user else None
        return super().create(data)

    def update(self, id: int, data: dict) -> CashTransferNote:
        """
        Actualiza una CashTransferNote solo si está en DRAFT.
        """
        note = self._get_note(id)
        self._ensure_draft(note)

        data["updated_by"] = g.current_user.id if g.current_user else None
        return super().update(id, data)

    def delete(self, id: int) -> bool:
        """
        Soft delete de una CashTransferNotes solo si está en DRAFT.
        """
        note = self._get_note(id)
        self._ensure_draft(note)

        note.is_active = False
        note.deleted_at = datetime.now(timezone.utc)
        note.updated_by = g.current_user.id if g.current_user else None
        db_session.commit()
        return

    # ------------------------------------------------------------
    # MÉTODOS DE NEGOCIO
    # ------------------------------------------------------------
    def confirm(self, id: int) -> CashTransferNote:
        """
        Confirma una CashTransferNote.

        Este servicio NO decide reglas de negocio ni valida invariantes
        de cuentas. Su única responsabilidad es:

        - Reunir toda la información del documento
        - Lanzar el movimiento de efectivo correspondiente
        - Si no hay errores, marcar el documento como CONFIRMED

        Todas las reglas de negocio (validación de balances,
        transferencias, invariantes contables, etc.) se validan y
        ejecutan exclusivamente en el cash_movements_service.
        """
        note = self._get_note(id)
        self._ensure_draft(note)

        if note.amount <= 0:
            raise BadRequestException(
                "Transfer amount must be greater than zero"
            )

        if note.from_cash_account_id == note.to_cash_account_id:
            raise BadRequestException(
                "Source and destination cash accounts must be different"
            )

        # --------------------------------------------------------
        # MOVIMIENTO DE CASH
        #
        # Se lanza el movimiento de efectivo pasando TODA la
        # información necesaria (documento y fecha).
        #
        # El cash_movements_service:
        # - interpreta el documento
        # - determina los débitos y créditos
        # - valida invariantes contables
        # - aplica los cambios o lanza excepción
        # --------------------------------------------------------
        cash_movements_service.apply_movement(aggregate=note, lines=None, date=note.date)

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
cash_transfer_notes_service = CashTransferNotesService()

# /src/app/services/cash_transfer_notes_service.py
