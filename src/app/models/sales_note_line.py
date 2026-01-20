# /src/app/models/sales_note_line.py
"""SalesNoteLine Model — v3.0

Representa una línea de producto dentro de un documento de venta.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base_model import BaseModel


class SalesNoteLine(BaseModel):
    """Línea de documento de venta."""

    __tablename__ = "sales_note_lines"
    
    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================

    sales_note_id: Mapped[int] = mapped_column(ForeignKey("sales_notes.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    quantity: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        data = super().to_dict() # Datos heredados
        data.update({"sales_note_id": self.sales_note_id, "product_id": self.product_id, "quantity": float(self.quantity), "unit_price": float(self.unit_price), "total_price": float(self.total_price)}) # Datos del modelo
        return data

# /src/app/models/sales_note_line.py