"""Authentication business logic."""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def register_user(
    db: Session, payload: UserCreate, allow_privileged: bool = False
) -> User:
    """Create a user.

    Public self-registration always creates a citizen, but a citizen may record
    their own home constituency. Only privileged callers (super admin) may set
    officer/mp/super_admin roles.
    """
    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    role = payload.role if allow_privileged else UserRole.citizen

    user = User(
        name=payload.name,
        email=str(payload.email),
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role=role,
        constituency_id=payload.constituency_id,
        home_state_id=payload.home_state_id,
        home_district_id=payload.home_district_id,
        home_constituency_id=payload.home_constituency_id,
        home_ward_id=payload.home_ward_id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled."
        )
    return user
