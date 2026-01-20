# /src/app/api/routers/stock_locations_router.py
from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.stock_locations_controller import stock_locations_controller

stock_locations_router = BaseRouter("stock_locations", stock_locations_controller).router

@stock_locations_router.get("/by_name/<string:name>")
def get_by_name(name):
    return stock_locations_controller.get_by_name(name)
# /src/app/api/routers/stock_locations_router.py