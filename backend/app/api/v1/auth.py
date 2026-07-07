"""Authentication endpoints."""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, Token
from app.schemas.user import UserCreate, UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Public self-registration. Always creates a CITIZEN account."""
    user = auth_service.register_user(db, payload, allow_privileged=False)
    token = create_access_token(user.id, user.role.value)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """JSON login used by the frontend."""
    user = auth_service.authenticate(db, str(payload.email), payload.password)
    token = create_access_token(user.id, user.role.value)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/token", response_model=Token)
def token(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """OAuth2 password flow — powers the Swagger 'Authorize' button.
    Use your email as the username."""
    user = auth_service.authenticate(db, form.username, form.password)
    access = create_access_token(user.id, user.role.value)
    return Token(access_token=access, user=UserOut.model_validate(user))


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):
    """Placeholder password-reset request (MVP).

    Always returns the same generic message regardless of whether the email
    exists, so account existence isn't leaked. Real email delivery is a future
    integration; nothing is sent yet.
    """
    return {
        "message": "If this email exists, password reset instructions will be sent."
    }


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
