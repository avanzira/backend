# /src/app/models/user.py
"""User Model — v3.0

Representa un usuario del sistema.

Notas:
- Usado por auth, security y auditoría
- Preferencias incluidas para frontend
- Fechas siempre normalizadas

Reglas:
- hash_password NUNCA se serializa
- Sin lógica de negocio
"""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import DateTime, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base_model import BaseModel
from src.app.core import UserRole
from src.app.core.utils.datetime_utils import dt_to_iso_z

class User(BaseModel):
    """Usuario persistente."""

    __tablename__ = "users"

    # ============================================================
    # IDENTIDAD
    # ============================================================

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rol: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)

    # ============================================================
    # PREFERENCIAS
    # ============================================================

    user_language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    user_theme: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ============================================================
    # SEGURIDAD
    # ============================================================

    hash_password: Mapped[str] = mapped_column(String(255), nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    password_changed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ============================================================
    # SERIALIZACIÓN
    # ============================================================

    def to_dict(self) -> dict:
        """Serializa el usuario para API.

        Seguridad:
        - No expone hash_password
        """

        data = super().to_dict()
        data.update({"username": self.username, "email": self.email, "rol": self.rol, "user_language": self.user_language, "user_theme": self.user_theme, "last_login": dt_to_iso_z(self.last_login), "password_changed_at": dt_to_iso_z(self.password_changed_at)})
        return data

# /src/app/models/user.py
