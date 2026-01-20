# /src/app/models/purchase_note_line.py
"""PurchaseNoteLine Model — v3.0

Representa una línea de producto dentro de un documento de compra.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base_model import BaseModel


class PurchaseNoteLine(BaseModel):
    """Línea de documento de compra."""

    __tablename__ = "purchase_note_lines"
    
    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================

    purchase_note_id: Mapped[int] = mapped_column(ForeignKey("purchase_notes.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    quantity: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        data = super().to_dict() # Datos heredados
        data.update({"purchase_note_id": self.purchase_note_id, "product_id": self.product_id, "quantity": float(self.quantity), "unit_price": float(self.unit_price), "total_price": float(self.total_price)}) # Datos del modelo
        return data

# /src/app/models/purchase_note_line.py