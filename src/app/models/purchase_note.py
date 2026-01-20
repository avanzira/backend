# /src/app/models/purchase_note.py
"""PurchaseNote Model — v3.0

Documento de compra a proveedor.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy import DateTime


from src.app.models.base_model import BaseModel
from src.app.core.utils.datetime_utils import dt_to_iso_z
from src.app.core import DocumentStatus

class PurchaseNote(BaseModel):
    """Documento de compra persistente."""

    __tablename__ = "purchase_notes"
    
    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================

    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[DocumentStatus] = mapped_column(SAEnum(DocumentStatus), nullable=False)

    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("total_amount >= paid_amount", name="ck_purchase_total_ge_paid"),
    )

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        """Serializa el cliente para exposición en API.

        Returns:
            dict: representación serializable del cliente.
        """

        data = super().to_dict() # Datos heredados
        data.update({"supplier_id": self.supplier_id, "date": dt_to_iso_z(self.date), "status": self.status, "total_amount": float(self.total_amount), "paid_amount": float(self.paid_amount)}) # Datos del modelo
        return data

# /src/app/models/purchase_note.py
