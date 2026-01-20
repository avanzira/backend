# /src/app/models/stock_location.py
"""StockLocation Model — v3.0

Representa una ubicación de stock.

Notas v3.0:
- NO existen movimientos como modelos persistentes (StockMovement no es tabla).
- Las consultas de movimientos son lógicas y viven en services.

Reglas:
- Sin lógica de negocio.
- Serialización consistente vía BaseModel.to_dict().
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base_model import BaseModel


class StockLocation(BaseModel):
    """Ubicación de stock persistente.

    Entidad que representa un lugar físico o lógico donde se almacena stock.

    Notas:
    - No distingue tipos de ubicación (empresa, cliente, etc.).
    - Las reglas de negocio que dependen del uso de la ubicación viven en services.
    """

    __tablename__ = "stock_locations"

    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        """Serializa la ubicación de stock para exposición en API.

        Returns:
            dict: representación serializable de la ubicación.
        """

        data = super().to_dict() # Datos heredados
        data.update({"name": self.name}) # Datos del modelo
        return data

# /src/app/models/stock_location.py
