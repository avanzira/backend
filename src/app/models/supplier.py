# /src/app/models/supplier.py
"""Supplier Model — v3.0

Representa un proveedor del sistema.

Reglas:
- Sin lógica de negocio.
- Serialización consistente vía BaseModel.to_dict().
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base_model import BaseModel


class Supplier(BaseModel):
    """Entidad proveedor persistente."""

    __tablename__ = "suppliers"

     # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    address: Mapped[str] = mapped_column(String(200), nullable=True)

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        """Serializa el cliente para exposición en API.

        Returns:
            dict: representación serializable del cliente.
        """

        data = super().to_dict() # Datos heredados
        data.update({"name": self.name, "phone": self.phone, "email": self.email, "address": self.address}) # Datos del modelo
        return data

# /src/app/models/supplier.py