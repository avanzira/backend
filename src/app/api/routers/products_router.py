# /src/app/api/routers/products_router.py
from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.products_controller import products_controller

products_router = BaseRouter("products", products_controller).router
# /src/app/api/routers/products_router.py