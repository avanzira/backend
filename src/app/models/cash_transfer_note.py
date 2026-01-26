# /src/app/models/cash_transfer_note.py
"""CashTransferNote Model — v3.0

Documento de transferencia de cash entre cuentas internas.

Regla de dominio:
- Esta transferencia nunca debe generar balance positivo en cuentas de proveedor.
- La validación se realiza en services.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy import DateTime


from src.app.models.base_model import BaseModel
from src.app.core import DocumentStatus
from src.app.core.utils.datetime_utils import dt_to_iso_z



class CashTransferNote(BaseModel):
    """Documento de transferencia de cash."""

    __tablename__ = "cash_transfer_notes"

    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================

    from_cash_account_id: Mapped[int | None] = mapped_column(ForeignKey("cash_accounts.id"), nullable=True)
    to_cash_account_id: Mapped[int | None] = mapped_column(ForeignKey("cash_accounts.id"), nullable=True)

    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[DocumentStatus] = mapped_column(SAEnum(DocumentStatus), nullable=False)

    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_cash_transfer_amount_positive"),
    )

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "from_cash_account_id": self.from_cash_account_id,
            "to_cash_account_id": self.to_cash_account_id,
            "date": dt_to_iso_z(self.date),
            "status": self.status,
            "amount": float(self.amount),
            "notes": self.notes,
        })
        return data

# /src/app/models/cash_transfer_note.py
