# /src/app/api/routers/cash_accounts_router.py
from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.cash_account_controller import cash_account_controller

cash_accounts_router = BaseRouter("cash_accounts", cash_account_controller).router

@cash_accounts_router.get("/by_name/<string:name>")
def get_by_name(name):
    return cash_account_controller.get_by_name(name)
# /src/app/api/routers/cash_accounts_router.py