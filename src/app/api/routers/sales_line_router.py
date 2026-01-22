# /src/app/api/routers/sales_line_router.py
from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.sales_line_controller import sales_line_controller

sales_line_router = BaseRouter("sales_lines", sales_line_controller).router

sales_line_router.post("/<int:sales_id>/lines")(sales_line_controller.create_line)
sales_line_router.get("/<int:sales_id>/lines")(sales_line_controller.get_lines)
sales_line_router.put("/<int:sales_id>/lines/<int:line_id>")(sales_line_controller.update_line)
sales_line_router.delete("/<int:sales_id>/lines/<int:line_id>")(sales_line_controller.delete_line)
sales_line_router.delete("/lines/<int:id>")(sales_line_controller.delete)
# /src/app/api/routers/sales_line_router.py
