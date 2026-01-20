# /src/app/models/cash_account.py
"""CashAccount Model — v3.0

Representa una cuenta de efectivo o bancaria del sistema.

Notas v3.0:
- El balance puede ser positivo o negativo según el tipo lógico de cuenta.
- Las reglas de dominio (empresa >= 0, proveedor <= 0) se validan en services.

Reglas:
- Sin lógica de negocio.
- Serialización consistente vía BaseModel.to_dict().
"""

from __future__ import annotations

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base_model import BaseModel


class CashAccount(BaseModel):
    """Cuenta de cash/banco persistente."""

    __tablename__ = "cash_accounts"

    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"name": self.name, "balance": float(self.balance)})
        return data

# /src/app/models/cash_account.py
