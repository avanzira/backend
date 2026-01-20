# /src/app/services/users_service.py

"""
UsersService — v3.0

Servicio de dominio para la gestión de usuarios del sistema.

⚠️ NO es un CRUD simple.

Responsabilidades:
- Crear usuarios con credenciales (password en claro → hash en servidor)
- Gestionar roles (solo admin)
- Cambiar contraseñas
- Aplicar reglas de seguridad críticas
- Proteger invariantes (último admin, auto-delete)

Cumple architecture_v3.0:
- Exporta una instancia
- Controllers importan la instancia
"""

from datetime import datetime, timezone
from flask import g

from src.app.services.base_service import BaseService
from src.app.models.user import User

from src.app.core import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UserRole,
)
from src.app.core.config.database import db_session

from src.app.security.password import hash_password, verify_password


class UsersService(BaseService):
    """
    Servicio de dominio para usuarios.

    Hereda BaseService y redefine create/update/delete
    por reglas explícitas de seguridad.
    """

    model = User

    # ------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------
    def _get_user(self, user_id: int) -> User:
        """
        Obtiene un usuario activo por ID o lanza excepción.
        """
        user = (
            db_session.query(User)
            .filter(User.id == user_id, User.is_active == True)
            .first()
        )
        if not user:
            raise NotFoundException("User not found")
        return user

    def _ensure_unique_username(self, username: str, user_id: int | None = None):
        """
        Garantiza que el username sea único.
        """
        q = db_session.query(User).filter(
            User.username == username,
            User.is_active == True,
        )
        if user_id:
            q = q.filter(User.id != user_id)

        if q.first():
            raise ForbiddenException("Username already exists")

    def _ensure_not_last_admin(self, user: User):
        """
        Impide borrar el último usuario admin del sistema.
        """
        if user.rol != UserRole.ADMIN:
            return

        total_admins = (
            db_session.query(User)
            .filter(
                User.rol == UserRole.ADMIN,
                User.is_active == True,
            )
            .count()
        )

        if total_admins <= 1:
            raise ForbiddenException("Cannot delete the last admin")

    # ------------------------------------------------------------
    # CRUD MODIFICADO
    # ------------------------------------------------------------
    def create(self, user: dict) -> User:
        """
        Crea un usuario con password hasheado en servidor.
        """
        username = user.get("username")
        password = user.get("password")
        rol = user.get("rol")

        if not username or not password or not rol:
            raise BadRequestException("username, password, and rol are required")

        self._ensure_unique_username(username)

        user["hash_password"] = hash_password(password)
        user["password_changed_at"] = datetime.now(timezone.utc)
        user.pop("password", None)

        user["created_by"] = g.current_user.id if g.current_user else None

        return super().create(user)

    def update(self, user_id: int, user: dict) -> User:
        """
        Actualiza datos del usuario respetando reglas de seguridad.
        """
        current = self._get_user(user_id)

        if "hash_password" in user or "password_changed_at" in user:
            raise ForbiddenException("Cannot modify password directly")

        if "username" in user:
            self._ensure_unique_username(user["username"], user_id)

        if "rol" in user:
            current_user = g.current_user
            if not current_user or current_user.rol != UserRole.ADMIN:
                raise ForbiddenException("Only admin can modify roles")

        updated = super().update(user_id, user)
        updated.updated_by = g.current_user.id

        db_session.commit()
        return updated

    def delete(self, user_id: int) -> User:
        """
        Soft delete de usuario con validaciones.
        """
        user = self._get_user(user_id)

        current_user = g.current_user
        if not current_user:
            raise ForbiddenException("Authentication required")

        if user.id == current_user.id:
            raise ForbiddenException("You cannot delete your own user")

        self._ensure_not_last_admin(user)

        user.is_active = False
        user.deleted_at = datetime.now(timezone.utc)
        user.updated_by = g.current_user.id

        db_session.commit()
        return

    # ------------------------------------------------------------
    # MÉTODOS DE NEGOCIO
    # ------------------------------------------------------------
    def change_password(self, user_id: int, old_password: str, new_password: str) -> User:
        """
        Cambia la contraseña de un usuario validando credenciales.
        """
        user = self._get_user(user_id)

        if not old_password or not new_password:
            raise BadRequestException("old_password and new_password are required")

        if not verify_password(old_password, user.hash_password):
            raise ForbiddenException("Old password is incorrect")

        if len(new_password) < 6:
            raise BadRequestException("New password must have at least 6 characters")

        user.hash_password = hash_password(new_password)
        user.password_changed_at = datetime.now(timezone.utc)
        user.updated_by = g.current_user.id

        db_session.commit()
        return user


# ------------------------------------------------------------
# INSTANCIA EXPORTADA (OBLIGATORIA)
# ------------------------------------------------------------
users_service = UsersService()

# /src/app/services/users_service.py
