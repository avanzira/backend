# /src/app/api/routers/users_router.py
from src.app.api.routers.base_router import BaseRouter
from src.app.controllers.user_controller import user_controller

users_router = BaseRouter("users", user_controller).router

users_router.post("/change-password")(user_controller.change_password)
# /src/app/api/routers/users_router.py