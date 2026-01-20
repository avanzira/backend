# /src/app/api/routers/auth_router.py
from flask import Blueprint, request
from src.app.controllers.auth_controller import auth_controller

auth_router = Blueprint("auth", __name__)

auth_router.post("/login")(auth_controller.login)

@auth_router.post("/refresh")
def refresh():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": "Missing refresh token"}, 401
    token = auth_header.replace("Bearer ", "").strip()
    return auth_controller.refresh(token)

auth_router.get("/me")(auth_controller.me)
# /src/app/api/routers/auth_router.py