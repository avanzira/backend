# /src/app/services/cash_movements_service.py

"""
CashMovementsService — v3.0

Servicio de dominio para ejecutar movimientos de efectivo.

⚠️ NO es un CRUD
⚠️ NO tiene modelo
⚠️ NO persiste movimientos
⚠️ NO conoce Documents ni cambia estados
⚠️ NO asume existencia de lines salvo que se le pasen explícitamente

Responsabilidad única:
- Aplicar efectos reales sobre CashAccount

Modelo operativo (cerrado v3.0):
Un movement es siempre atómico y se define como:
(delta, cash_account_id)

Casos permitidos:
1) Compra:
   - DEME cash ↓ paid_amount
   - Supplier cash ↓ (total_amount - paid_amount)

2) Venta:
   - DEME cash ↑ total_amount

3) Transferencia:
   - from_cash_account ↓ amount
   - to_cash_account ↑ amount

Auditoría:
- updated_at = date (fecha del note que lanza el movement)
- updated_by = g.current_user.id
"""

from datetime import datetime
from decimal import Decimal
from flask import g

from src.app.models.cash_account import CashAccount
from src.app.models.supplier import Supplier
from src.app.models.purchase_note import PurchaseNote
from src.app.models.sales_note import SalesNote
from src.app.models.cash_transfer_note import CashTransferNote

from src.app.core import BadRequestException, ForbiddenException, db_session
from src.app.core.config.settings import settings


class CashMovementsService:
    """
    Servicio puro de ejecución de movimientos de efectivo.
    """

    # ------------------------------------------------------------
    # API PÚBLICA
    # ------------------------------------------------------------
    def apply_movement(self, aggregate, lines: list | None, date: datetime) -> None:
        """
        Ejecuta un movimiento de efectivo en función del aggregate recibido.
        """

        if isinstance(aggregate, PurchaseNote):
            self._apply_purchase(aggregate, date)
            return

        if isinstance(aggregate, SalesNote):
            self._apply_sale(aggregate, date)
            return

        if isinstance(aggregate, CashTransferNote):
            self._apply_cash_transfer(aggregate, date)
            return

        raise BadRequestException("Unsupported aggregate for cash movement")

    # ------------------------------------------------------------
    # PURCHASE
    # ------------------------------------------------------------
    def _apply_purchase(self, purchase: PurchaseNote, date: datetime) -> None:
        """
        Salida de efectivo de DEME y registro de deuda con proveedor si aplica.
        """

        if purchase.paid_amount <= 0:
            return

        deme_account = self._get_deme_account()

        self._apply_delta(
            account=deme_account,
            delta=Decimal(-purchase.paid_amount),
            forbid_negative=True,
            forbid_positive=False,
            date=date,
        )

        if purchase.total_amount > purchase.paid_amount:
            supplier_account = self._get_supplier_account(purchase.supplier_id)
            debt = Decimal(purchase.total_amount - purchase.paid_amount)

            self._apply_delta(
                account=supplier_account,
                delta=-debt,
                forbid_negative=False,
                forbid_positive=False,
                date=date,
            )

    # ------------------------------------------------------------
    # SALE
    # ------------------------------------------------------------
    def _apply_sale(self, sale: SalesNote, date: datetime) -> None:
        """
        Entrada de efectivo en la cuenta DEME.
        """

        if sale.total_amount <= 0:
            return

        deme_account = self._get_deme_account()

        self._apply_delta(
            account=deme_account,
            delta=Decimal(sale.total_amount),
            forbid_negative=False,
            forbid_positive=False,
            date=date,
        )

    # ------------------------------------------------------------
    # CASH TRANSFER
    # ------------------------------------------------------------
    def _apply_cash_transfer(self, transfer: CashTransferNote, date: datetime) -> None:
        """
        Transferencia de efectivo entre cuentas.
        """

        from_account = self._get_account(transfer.from_cash_account_id)
        to_account = self._get_account(transfer.to_cash_account_id)

        self._apply_delta(
            account=from_account,
            delta=Decimal(-transfer.amount),
            forbid_negative=True,
            forbid_positive=False,
            date=date,
        )

        self._apply_delta(
            account=to_account,
            delta=Decimal(transfer.amount),
            forbid_negative=False,
            forbid_positive=False,
            date=date,
        )

    # ------------------------------------------------------------
    # DELTA CORE
    # ------------------------------------------------------------
    def _apply_delta(self, account: CashAccount, delta: Decimal, forbid_negative: bool, forbid_positive: bool, date: datetime) -> None:
        """
        Aplica un delta de efectivo sobre una CashAccount.
        """

        new_balance = account.balance + delta

        if forbid_negative and new_balance < 0:
            raise ForbiddenException("CashAccount balance cannot become negative")

        if forbid_positive and new_balance > 0:
            raise ForbiddenException("CashAccount balance cannot become positive")

        account.balance = new_balance
        account.updated_at = date
        account.updated_by = g.current_user.id

        db_session.flush()

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_account(self, account_id: int) -> CashAccount:
        account = (
            db_session.query(CashAccount)
            .filter(
                CashAccount.id == account_id,
                CashAccount.is_active == True,
            )
            .first()
        )
        if not account:
            raise BadRequestException("CashAccount not found")
        return account

    def _get_deme_account(self) -> CashAccount:
        account = (
            db_session.query(CashAccount)
            .filter(
                CashAccount.name == settings.DEME_CASH_ACCOUNT_NAME,
                CashAccount.is_active == True,
            )
            .first()
        )
        if not account:
            raise BadRequestException("DEME CashAccount not found")
        return account

    def _get_supplier_account(self, supplier_id: int) -> CashAccount:
        account = (
            db_session.query(CashAccount)
            .filter(
                CashAccount.name == f"supplier_{supplier_id}_cash",
                CashAccount.is_active == True,
            )
            .first()
        )
        if not account:
            raise BadRequestException("Supplier cash account not found")
        return account


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
cash_movements_service = CashMovementsService()

# /src/app/services/cash_movements_service.py
