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


# Default demo login accounts, seeded on startup so a freshly deployed database
# (tables auto-created but not run through `init_db`) still has working logins.
_DEMO_USERS = [
    ("Platform Admin", "admin@loktra.ai", "admin123", UserRole.super_admin),
    ("Demo MP", "mp@loktra.ai", "mp123456", UserRole.mp),
    ("Demo Officer", "officer@loktra.ai", "officer123", UserRole.officer),
    ("Demo Citizen", "citizen@loktra.ai", "citizen123", UserRole.citizen),
]


def ensure_demo_users(db: Session) -> int:
    """Create the demo accounts if missing, and CORRECT an existing demo account
    whose role / password / active flag has drifted (e.g. `admin@loktra.ai` left as
    a citizen after a public signup). Never duplicates an email; uses the same
    password hashing as registration/login. Returns how many rows changed."""
    changed = 0
    for name, email, password, role in _DEMO_USERS:
        user = get_user_by_email(db, email)
        if user is None:
            db.add(
                User(
                    name=name,
                    email=email,
                    hashed_password=hash_password(password),
                    role=role,
                    is_active=True,
                )
            )
            changed += 1
            continue

        fixed = False
        if user.role != role:            # <- fixes the demo-role mismatch
            user.role = role
            fixed = True
        if not user.is_active:
            user.is_active = True
            fixed = True
        if not verify_password(password, user.hashed_password):
            user.hashed_password = hash_password(password)
            fixed = True
        if fixed:
            changed += 1
    if changed:
        db.commit()
    return changed


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
