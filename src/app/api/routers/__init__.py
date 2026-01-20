# /src/app/api/routers/__init__.py

from .auth_router import auth_router

# USERS Y ENTIDADES MAESTRAS
from .users_router import users_router
from .products_router import products_router
from .customers_router import customers_router
from .suppliers_router import suppliers_router

# DOCUMENTOS DE COMPRA
from .purchase_notes_router import purchase_notes_router
from .purchase_line_router import purchase_line_router

# DOCUMENTOS DE VENTA
from .sales_notes_router import sales_notes_router
from .sales_line_router import sales_line_router

# STOCK
from .stock_locations_router import stock_locations_router
from .stock_product_locations_router import stock_product_locations_router
from .stock_deposit_notes_router import stock_deposit_notes_router

# CASH
from .cash_accounts_router import cash_accounts_router
from .cash_transfer_notes_router import cash_transfer_notes_router

# SISTEMA
from .backup_router import backup_router

# /src/app/api/routers/__init__.py
