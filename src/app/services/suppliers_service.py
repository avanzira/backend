# /src/app/services/suppliers_service.py

"""
SuppliersService — v3.0

Servicio de dominio para la gestión de proveedores.

Responsabilidades:
- CRUD de Supplier
- Crear automáticamente su CashAccount asociada
- Garantizar unicidad del nombre
- Proteger la integridad económica

Reglas de dominio:
- Un Supplier tiene exactamente una CashAccount
- La CashAccount se crea automáticamente al crear el Supplier
- Un Supplier NO puede borrarse si:
  - existen PurchaseNotes asociadas
  - su CashAccount.balance != 0
- Soft delete con is_active + deleted_at
"""

from datetime import datetime, timezone
from flask import g
from src.app.core import UserRole

from src.app.services.base_service import BaseService
from src.app.services.cash_accounts_service import cash_accounts_service

from src.app.models.supplier import Supplier
from src.app.models.purchase_note import PurchaseNote
from src.app.models.cash_account import CashAccount

from src.app.core import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    db_session,
)


class SuppliersService(BaseService):
    """
    Servicio de dominio para Supplier.
    """

    model = Supplier

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_supplier(self, supplier_id: int) -> Supplier:
        """
        Obtiene un proveedor activo por ID o lanza excepción.
        """
        supplier = (
            db_session.query(Supplier)
            .filter(
                Supplier.id == supplier_id,
                Supplier.is_active == True,
            )
            .first()
        )
        if not supplier:
            raise NotFoundException("Supplier not found")
        return supplier

    def _get_cash_account(self, supplier: Supplier) -> CashAccount:
        """
        Obtiene la CashAccount asociada a un proveedor.
        """
        account = (
            db_session.query(CashAccount)
            .filter(
                CashAccount.name == f"supplier_{supplier.id}_cash",
                CashAccount.is_active == True,
            )
            .first()
        )
        if not account:
            raise NotFoundException("Supplier cash account not found")
        return account

    def _ensure_unique_name(self, name: str, supplier_id: int | None = None) -> None:
        """
        Garantiza que el nombre del proveedor sea único.
        """
        q = db_session.query(Supplier).filter(
            Supplier.name == name,
            Supplier.is_active == True,
        )
        if supplier_id:
            q = q.filter(Supplier.id != supplier_id)

        if q.first():
            raise ForbiddenException("Supplier name already exists")

    def _ensure_supplier_deletable(self, supplier: Supplier) -> None:
        """
        Valida que un proveedor pueda eliminarse sin romper integridad.

        Reglas:
        - No debe haber PurchaseNotes asociadas
        - La CashAccount.balance debe ser 0
        """

        # 1) No debe haber compras asociadas
        purchases_count = db_session.query(PurchaseNote).filter(
            PurchaseNote.supplier_id == supplier.id
        ).count()

        if purchases_count > 0:
            raise ForbiddenException(
                "Supplier cannot be deleted because purchases exist"
            )

        # 2) La cuenta de efectivo debe estar saldada
        account = self._get_cash_account(supplier)
        if account.balance != 0:
            raise ForbiddenException(
                "Supplier cannot be deleted because cash balance is not zero"
            )

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------
    def create(self, data: dict) -> Supplier:
        """
        Crea un proveedor y su CashAccount asociada.
        """
        name = data.get("name")
        if not name:
            raise BadRequestException("Supplier name is required")

        self._ensure_unique_name(name)

        data["created_by"] = g.current_user.id if g.current_user else None
        supplier = super().create(data)

        # Creación automática de CashAccount asociada
        account = cash_accounts_service.create(
            {
                "name": f"supplier_{supplier.id}_cash",
            }
        )

        supplier.updated_by = g.current_user.id if g.current_user else None

        db_session.commit()
        return supplier

    def update(self, supplier_id: int, data: dict) -> Supplier:
        """
        Actualiza un proveedor garantizando unicidad del nombre.
        """
        supplier = self._get_supplier(supplier_id)

        if "name" in data:
            self._ensure_unique_name(data["name"], supplier.id)

        data["updated_by"] = g.current_user.id if g.current_user else None
        return super().update(supplier_id, data)

    def delete(self, supplier_id: int) -> bool:
        """
        Soft delete de proveedor con validaciones de integridad económica.
        """
        supplier = self._get_supplier(supplier_id)
        self._ensure_supplier_deletable(supplier)

        supplier.is_active = False
        supplier.deleted_at = datetime.now(timezone.utc)
        supplier.updated_by = g.current_user.id if g.current_user else None

        db_session.commit()
        return


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
suppliers_service = SuppliersService()

# /src/app/services/suppliers_service.py
