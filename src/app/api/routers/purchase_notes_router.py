# /src/app/api/routers/purchase_notes_router.py
from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.purchase_notes_controller import purchase_notes_controller

purchase_notes_router = BaseRouter("purchase_notes", purchase_notes_controller).router

purchase_notes_router.post("/<int:id>/confirm")(purchase_notes_controller.confirm)
# /src/app/api/routers/purchase_notes_router.py
