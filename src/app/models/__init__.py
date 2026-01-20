# /src/app/models/__init__.py
"""Models Package — v3.0

Punto de exportación controlado de modelos ORM persistentes.

Reglas:
- Solo exporta modelos persistentes (tablas reales).
- NO exporta "movimientos" como modelos (v3.0 elimina StockMovement/CashMovement como tablas).
- Mantener esta lista alineada con /src/app/db/base.py.

Uso:
- Importar modelos desde este paquete es opcional.
- El registro ORM se fuerza en /src/app/db/base.py.
"""

# ============================================================
# BASE
# ============================================================

from .base_model import BaseModel

# ============================================================
# ENTIDADES
# ============================================================

from .user import User
from .customer import Customer
from .supplier import Supplier
from .product import Product

# ============================================================
# STOCK
# ============================================================

from .stock_location import StockLocation
from .stock_product_location import StockProductLocation

# ============================================================
# CASH
# ============================================================

from .cash_account import CashAccount

# ============================================================
# DOCUMENTOS
# ============================================================

from .purchase_note import PurchaseNote
from .purchase_note_line import PurchaseNoteLine
from .sales_note import SalesNote
from .sales_note_line import SalesNoteLine
from .cash_transfer_note import CashTransferNote
from .stock_deposit_note import StockDepositNote

__all__ = ["BaseModel", "User", "Customer", "Supplier", "Product", "StockLocation", "StockProductLocation", "CashAccount", "PurchaseNote", "PurchaseNoteLine", "SalesNote", "SalesNoteLine", "CashTransferNote", "StockDepositNote"]

# /src/app/models/__init__.py