# /src/app/models/base_model.py
"""
BaseModel — v3.0

Modelo base del sistema DemeArizOil.
Define:
- Identidad
- Auditoría
- Soft delete
- Serialización base

TODOS los modelos persistentes heredan de esta clase.
"""
from datetime import datetime, timezone
from sqlalchemy import DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.app.db.base import Base
from src.app.core.utils.datetime_utils import dt_to_iso_z

class BaseModel(Base):
    """
    Clase base para todos los modelos ORM persistentes.
    """

    __abstract__ = True

    # ------------------------------------------------------------
    # CAMPOS BASE
    # ------------------------------------------------------------
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ------------------------------------------------------------
    # SERIALIZACIÓN
    # ------------------------------------------------------------
    def to_dict(self) -> dict:
        """
        Serializa los campos base del modelo.

        Este método:
        - DEBE ser extendido por los modelos hijos
        - NUNCA debe ser eliminado
        """
        return {
            "id": self.id,
            "is_active": self.is_active,
            "created_at": dt_to_iso_z(self.created_at),
            "updated_at": dt_to_iso_z(self.updated_at),
            "deleted_at": dt_to_iso_z(self.deleted_at),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
        }
# /src/app/models/base_model.py
