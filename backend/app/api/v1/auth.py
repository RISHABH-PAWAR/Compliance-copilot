"""Authentication Endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, TokenResponse, TokenRefresh, UserResponse

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(credentials)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefresh, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh_token(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
