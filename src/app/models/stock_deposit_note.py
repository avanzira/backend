# /src/app/models/stock_deposit_note.py
"""StockDepositNote Model — v3.0

Documento de movimiento de stock entre ubicaciones.

Notas v3.0:
- Persiste cantidades ni productos.
- El impacto real en stock se calcula en stock_deposit_note_service, y se refleja en el quantity de StockProductLocation

Reglas:
- Sin lógica de negocio.
- Serialización consistente vía BaseModel.to_dict().
"""

from __future__ import annotations

from sqlalchemy import Date, ForeignKey, String, Numeric, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from sqlalchemy import DateTime



from src.app.models.base_model import BaseModel
from src.app.core.utils.datetime_utils import dt_to_iso_z
from src.app.core import DocumentStatus

class StockDepositNote(BaseModel):
    """Documento de depósito en la ubicación del cliente."""

    __tablename__ = "stock_deposit_notes"

    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================

    from_stock_location_id: Mapped[int | None] = mapped_column(ForeignKey("stock_locations.id"), nullable=True)
    to_stock_location_id: Mapped[int | None] = mapped_column(ForeignKey("stock_locations.id"), nullable=True)

    date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    quantity: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(SAEnum(DocumentStatus), nullable=False)

    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({"from_stock_location_id": self.from_stock_location_id,"to_stock_location_id": self.to_stock_location_id,"date": dt_to_iso_z(self.date), "product_id": self.product_id, "quantity": float(self.quantity),"status": self.status,"notes": self.notes})
        return data

# /src/app/models/stock_deposit_note.py
