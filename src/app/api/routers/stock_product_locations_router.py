# /src/app/api/routers/stock_product_locations_router.py
from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.stock_product_locations_controller import stock_product_locations_controller

stock_product_locations_router = BaseRouter("stock_product_locations", stock_product_locations_controller).router
# /src/app/api/routers/stock_product_locations_router.py