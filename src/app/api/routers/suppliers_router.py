# /src/app/api/routers/suppliers_router.py
from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.suppliers_controller import suppliers_controller

suppliers_router = BaseRouter("suppliers", suppliers_controller).router
# /src/app/api/routers/suppliers_router.py