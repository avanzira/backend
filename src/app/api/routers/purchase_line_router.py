# /src/app/api/routers/purchase_line_router.py
from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.purchase_line_controller import purchase_line_controller

purchase_line_router = BaseRouter("purchase_lines", purchase_line_controller).router

purchase_line_router.post("/<int:purchase_id>/lines")(purchase_line_controller.create_line)
purchase_line_router.get("/<int:purchase_id>/lines")(purchase_line_controller.get_all)
purchase_line_router.delete("/lines/<int:id>")(purchase_line_controller.delete)
# /src/app/api/routers/purchase_line_router.py
