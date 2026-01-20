# /src/app/core/enum.py
"""Domain enum — v3.0

Fuente única de verdad para valores discretos del dominio.

Reglas:
- Los enum NO son modelos ORM
- Los enum NO se persisten por sí mismos
- Son usados por models y services
- Evitan strings mágicos en el código

Referencia:
- architecture_v3.0.md
- business_logic_v3.0.md
"""

from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    """Roles de usuario del sistema."""

    ADMIN = "ADMIN"
    USER = "USER"


class DocumentStatus(str, Enum):
    """Estados de un documento de negocio."""

    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"


class StockMovementType(str, Enum):
    """Tipos lógicos de movimiento de stock.

    NOTA:
    - Este enum NO forma parte del schema
    - Se usa solo en services para calcular efectos
    """

    PURCHASE = "PURCHASE"
    SALE = "SALE"
    TRANSFER = "TRANSFER"
    ADJUSTMENT = "ADJUSTMENT"

# /src/app/core/enum.py