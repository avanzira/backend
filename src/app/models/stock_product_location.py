# /src/app/models/stock_product_location.py
"""StockProductLocation Model — v3.0

Representa el stock de un producto en una ubicación concreta.

Notas v3.0:
- Las actualizaciones de quantity se realizan en services.
- Este modelo es la fuente persistente del "stock actual".

Reglas:
- Sin lógica de negocio.
- Serialización consistente vía BaseModel.to_dict().
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.models.base_model import BaseModel


class StockProductLocation(BaseModel):
    """Stock por producto y ubicación (tabla persistente)."""

    __tablename__ = "stock_product_locations"

    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    stock_location_id: Mapped[int] = mapped_column(ForeignKey("stock_locations.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("stock_location_id", "product_id", name="uq_stock_product_location"),
        CheckConstraint("quantity >= 0", name="ck_stock_quantity_non_negative"),
    )

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        """Serializa el stock (producto/ubicación) para exposición en API.

        Returns:
            dict: representación serializable del stock.
        """

        data = super().to_dict()
        data.update({"product_id": self.product_id, "stock_location_id": self.stock_location_id, "quantity": float(self.quantity)})
        return data

# /src/app/models/stock_product_location.py