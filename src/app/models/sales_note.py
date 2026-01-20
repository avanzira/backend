# /src/app/models/sales_note.py
"""SalesNote Model — v3.0

Documento de venta a cliente.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy import DateTime


from src.app.models.base_model import BaseModel
from src.app.core.utils.datetime_utils import dt_to_iso_z
from src.app.core import DocumentStatus

class SalesNote(BaseModel):
    """Documento de venta persistente."""

    __tablename__ = "sales_notes"
    
    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    status: Mapped[DocumentStatus] = mapped_column(SAEnum(DocumentStatus), nullable=False)

    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("total_amount = paid_amount", name="ck_sales_total_eq_paid"),
    )

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        data = super().to_dict() # Datos heredados
        data.update({"customer_id": self.customer_id, "date": dt_to_iso_z(self.date), "status": self.status, "total_amount": float(self.total_amount), "paid_amount": float(self.paid_amount)}) # Datos del modelo
        return data

# /src/app/models/sales_note.py
