# /src/app/api/routers/sales_notes_router.py
from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.sales_notes_controller import sales_notes_controller

sales_notes_router = BaseRouter("sales_notes", sales_notes_controller).router

sales_notes_router.post("/<int:id>/confirm")(sales_notes_controller.confirm)
# /src/app/api/routers/sales_notes_router.py
