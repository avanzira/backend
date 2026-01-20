# /src/app/services/cash_accounts_service.py

"""
CashAccountsService — v3.0

Servicio de dominio para la gestión de cuentas de efectivo.

⚠️ NO es un CRUD simple.

Responsabilidades:
- Crear cuentas de efectivo
- Consultar cuentas por nombre
- Proteger la integridad del balance
- Impedir el borrado de cuentas con balance distinto de 0

Reglas de dominio:
- NO existen modelos de movimientos en v3.0
- Una CashAccount solo puede soft-deletearse si su balance es 0
- El estado del registro se controla exclusivamente con is_active
"""

from datetime import datetime, timezone
from flask import g

from src.app.services.base_service import BaseService
from src.app.models.cash_account import CashAccount

from src.app.core import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from src.app.core.config.database import db_session


class CashAccountsService(BaseService):
    """
    Servicio de dominio para CashAccount.
    """

    model = CashAccount

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_account(self, account_id: int) -> CashAccount:
        """
        Obtiene una cuenta activa por ID o lanza excepción.
        """
        account = (
            db_session.query(CashAccount)
            .filter(CashAccount.id == account_id, CashAccount.is_active == True)
            .first()
        )
        if not account:
            raise NotFoundException("CashAccount not found")
        return account

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------
    def create(self, data: dict) -> CashAccount:
        """
        Crea una cuenta de efectivo validando unicidad de nombre.
        """
        name = data.get("name")
        if not name:
            raise BadRequestException("CashAccount name is required")

        exists = db_session.query(CashAccount).filter(
            CashAccount.name == name,
            CashAccount.is_active == True,
        ).first()

        if exists:
            raise ForbiddenException("CashAccount name already exists")

        return super().create(data)

    def delete(self, account_id: int) -> bool:
        """
        Soft delete de cuenta de efectivo.

        Regla:
        - Solo se permite si balance == 0
        """
        account = self._get_account(account_id)

        if float(account.balance or 0) != 0:
            raise ForbiddenException(
                "CashAccount cannot be deleted because balance is not zero"
            )

        account.is_active = False
        account.deleted_at = datetime.now(timezone.utc)
        account.updated_by = g.current_user.id

        db_session.commit()
        return
    # ------------------------------------------------------------
    # MÉTODOS DE NEGOCIO
    # ------------------------------------------------------------
    def get_by_name(self, name: str) -> CashAccount:
        """
        Obtiene una cuenta de efectivo por nombre.
        """
        account = (
            db_session.query(CashAccount)
            .filter(CashAccount.name == name, CashAccount.is_active == True)
            .first()
        )
        if not account:
            raise NotFoundException("CashAccount not found")
        return account


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
cash_accounts_service = CashAccountsService()

# /src/app/services/cash_accounts_service.py
