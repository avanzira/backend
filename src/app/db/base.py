# /src/app/db/base.py
"""
Declarative Base — v3.0

Base declarativa centralizada de SQLAlchemy para el backend DemeArizOil.

Responsabilidad:
- Definir la clase Base común para todos los modelos ORM
- Forzar el registro de TODOS los modelos persistentes del sistema

IMPORTANTE (regla crítica de SQLAlchemy):
- SQLAlchemy SOLO crea tablas de los modelos que han sido importados
- Si un modelo no se importa aquí, su tabla NO se crea en la base de datos

Decisiones de arquitectura v3.0:
- Solo se importan MODELOS PERSISTENTES
- Los movimientos (StockMovement, CashMovement) NO existen como tablas
- Los documentos de negocio (PurchaseNote, SalesNote, StockDepositNotes,
  CashTransferNote, etc.) SÍ existen como modelos ORM

Referencia normativa:
- architecture_v3.0.md
- business_logic_v3.0.md
"""

from sqlalchemy.orm import declarative_base

# ============================================================
# BASE DECLARATIVA
# ============================================================
# Todos los modelos ORM del sistema DEBEN heredar de esta Base.
Base = declarative_base()

# ============================================================
# REGISTRO DE MODELOS ORM (OBLIGATORIO)
# ============================================================
# NOTA CRÍTICA:
# - Estos imports NO son decorativos
# - Su único propósito es registrar los modelos en el metadata de SQLAlchemy
# - El orden no es relevante, pero la lista debe estar COMPLETA

# -----------------
# USUARIOS Y ENTIDADES MAESTRAS
# -----------------
from src.app.models.user import User
from src.app.models.product import Product
from src.app.models.customer import Customer
from src.app.models.supplier import Supplier

# -----------------
# STOCK
# -----------------
# Ubicaciones y stock por producto
from src.app.models.stock_location import StockLocation
from src.app.models.stock_product_location import StockProductLocation

# Documento v3.0: depósito de stock físico
from src.app.models.stock_deposit_note import StockDepositNote

# -----------------
# CASH
# -----------------
# Cuentas internas de cash
from src.app.models.cash_account import CashAccount

# Documento v3.0: transferencia de dinero entre cuentas internas
from src.app.models.cash_transfer_note import CashTransferNote

# -----------------
# DOCUMENTOS DE COMPRA
# -----------------
from src.app.models.purchase_note import PurchaseNote
from src.app.models.purchase_note_line import PurchaseNoteLine

# -----------------
# DOCUMENTOS DE VENTA
# -----------------
from src.app.models.sales_note import SalesNote
from src.app.models.sales_note_line import SalesNoteLine

# /src/app/db/base.py
