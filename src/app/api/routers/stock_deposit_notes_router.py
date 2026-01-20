# /src/app/api/routers/stock_deposit_notes_router.py
"""
stock_deposit_notes router — v3.0
"""

from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.stock_deposit_notes_controller import (stock_deposit_notes_controller)

stock_deposit_notes_router = BaseRouter("stock_deposit_notes", stock_deposit_notes_controller).router


@stock_deposit_notes_router.post("/<int:id>/confirm")
def confirm(id: int):
    """
    Confirma un StockDepositNotes.
    """
    return stock_deposit_notes_controller.confirm(id)

# /src/app/api/routers/stock_deposit_notes_router.py
