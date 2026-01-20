# /src/app/api/routers/customers_router.py
from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.customers_controller import customers_controller

customers_router = BaseRouter("customers", customers_controller).router
# /src/app/api/routers/customers_router.py