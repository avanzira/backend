# /src/app/models/product.py
"""Product Model — v3.0

Representa un producto comercializado por el sistema.

Reglas:
- Sin lógica de negocio.
- cost_average se gestiona en services.
- Serialización consistente vía BaseModel.to_dict().
"""

from __future__ import annotations

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.models.base_model import BaseModel


class Product(BaseModel):
    """Producto persistente."""

    __tablename__ = "products"

    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================

    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    unit_measure: Mapped[str] = mapped_column(String(50), nullable=False)
    is_inventory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cost_average: Mapped[float] = mapped_column(Numeric(18, 6), default=0, nullable=False)

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        """Serializa el producto para exposición en API.

        Returns:
            dict: representación serializable del producto.
        """

        data = super().to_dict() # Datos heredados
        data.update({"name": self.name, "unit_measure": self.unit_measure, "is_inventory": self.is_inventory, "cost_average": float(self.cost_average)}) # Datos del modelo
        return data

# /src/app/models/product.py