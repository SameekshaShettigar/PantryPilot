from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth import get_current_user

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }
    
    
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        (User.username == user_data.username)
        | (User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    hashed_password = hash_password(user_data.password)

    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if user is None or not verify_password(
        user_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }