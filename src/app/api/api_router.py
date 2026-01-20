# /src/app/api/api_router.py
"""
API Router — v3.0

Router raíz de la API del backend DemeArizOil.

Este archivo es el punto central de exposición HTTP del sistema.
Aquí NO se implementa lógica de negocio ni seguridad: únicamente
se registran los routers de cada dominio/documento.

Decisiones clave:
- El prefijo global de la API se define en settings.API_PREFIX
- Todas las rutas pasan por el middleware de seguridad
- Las rutas públicas se declaran en settings.PUBLIC_PATHS
- Este archivo debe reflejar TODOS los documentos existentes del sistema

Referencia normativa:
- architecture_v3.0.md
"""

from __future__ import annotations

# Blueprint es el mecanismo de Flask para agrupar rutas
from flask import Blueprint

# Settings centraliza prefijos y configuración global
from src.app.core.config.settings import settings

# ============================================================
# IMPORTS DE ROUTERS
# ============================================================
# Cada router representa un dominio o documento del sistema.
# Este archivo SOLO los importa y los registra.
# No debe existir lógica adicional aquí.

# AUTH
# Login / refresh (rutas públicas)
from src.app.api.routers.auth_router import auth_router

# USERS Y ENTIDADES MAESTRAS
# CRUD básicos del sistema
from src.app.api.routers.users_router import users_router
from src.app.api.routers.products_router import products_router
from src.app.api.routers.customers_router import customers_router
from src.app.api.routers.suppliers_router import suppliers_router

# DOCUMENTOS DE COMPRA
# Albaranes de compra y sus líneas
from src.app.api.routers.purchase_notes_router import purchase_notes_router
from src.app.api.routers.purchase_line_router import purchase_line_router

# DOCUMENTOS DE VENTA
# Albaranes de venta y sus líneas
from src.app.api.routers.sales_notes_router import sales_notes_router
from src.app.api.routers.sales_line_router import sales_line_router

# STOCK
# Ubicaciones de stock y stock por producto/ubicación
from src.app.api.routers.stock_locations_router import stock_locations_router
from src.app.api.routers.stock_product_locations_router import stock_product_locations_router

# Documento v3.0: depósito de stock físico
# (puede venir de proveedor, cliente o ajuste operativo)
from src.app.api.routers.stock_deposit_notes_router import stock_deposit_notes_router

# CASH
# Cuentas de cash internas de la empresa
from src.app.api.routers.cash_accounts_router import cash_accounts_router

# Documento v3.0: transferencia de dinero entre cuentas internas
from src.app.api.routers.cash_transfer_notes_router import cash_transfer_notes_router

# SISTEMA
# Operaciones técnicas del sistema (backup, restore, etc.)
from src.app.api.routers.backup_router import backup_router

# ============================================================
# BLUEPRINTS
# ============================================================
# El prefijo (/api) NO se hardcodea aquí.
# Se obtiene siempre desde settings para permitir cambios futuros
# (por ejemplo /api/v1) sin tocar routers.
api_router = Blueprint("api", __name__, url_prefix=settings.API_PREFIX)

# REGISTRO DE ROUTERS
# Agrupado por dominio para facilitar lectura y mantenimiento.

# AUTH (rutas públicas)
api_router.register_blueprint(auth_router, url_prefix="/auth")

# USERS
api_router.register_blueprint(users_router, url_prefix="/users")

# ENTIDADES MAESTRAS
api_router.register_blueprint(products_router, url_prefix="/products")
api_router.register_blueprint(customers_router, url_prefix="/customers")
api_router.register_blueprint(suppliers_router, url_prefix="/suppliers")

# PURCHASE NOTES + LINES
# Las líneas comparten prefijo con su documento padre
api_router.register_blueprint(purchase_notes_router, url_prefix="/purchase_notes")
api_router.register_blueprint(purchase_line_router, url_prefix="/purchase_notes")

# SALES NOTES + LINES
api_router.register_blueprint(sales_notes_router, url_prefix="/sales_notes")
api_router.register_blueprint(sales_line_router, url_prefix="/sales_notes")

# STOCK
# Documentos, ubicaciones y consultas
api_router.register_blueprint(stock_locations_router, url_prefix="/stock_locations")
api_router.register_blueprint(stock_product_locations_router, url_prefix="/stock_product_locations")
api_router.register_blueprint(stock_deposit_notes_router, url_prefix="/stock_deposit_notes")

# CASH
# Documentos, cuentas y consultas
api_router.register_blueprint(cash_accounts_router, url_prefix="/cash_accounts")
api_router.register_blueprint(cash_transfer_notes_router, url_prefix="/cash_transfer_notes")

# SISTEMA
api_router.register_blueprint(backup_router, url_prefix="/backup")

# /src/app/api/api_router.py
