"""Reusable FastAPI dependencies for auth + RBAC."""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole

# tokenUrl powers the "Authorize" button in Swagger UI.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/token"
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise credentials_exc

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exc
    return user


def require_roles(*roles: UserRole):
    """Dependency factory: allow only the given roles."""

    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this action.",
            )
        return user

    return _dep


# Named shortcuts for readability in routers.
require_citizen = require_roles(UserRole.citizen)
require_officer = require_roles(UserRole.officer, UserRole.super_admin)
require_mp = require_roles(UserRole.mp, UserRole.super_admin)
require_admin = require_roles(UserRole.super_admin)
require_staff = require_roles(
    UserRole.officer, UserRole.mp, UserRole.super_admin
)
