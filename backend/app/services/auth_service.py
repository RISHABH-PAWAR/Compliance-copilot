"""Authentication Service"""
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.sql.user import User
from app.models.sql.audit_trail import AuditTrail
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, user_data: UserCreate) -> TokenResponse:
        # Check if email already exists
        existing = self.db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            company_id=user_data.company_id,
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Log audit trail
        self._log_audit(user.id, "user_registered", "user", str(user.id))

        return self._generate_tokens(user)

    def login(self, credentials: UserLogin) -> TokenResponse:
        user = self.db.query(User).filter(User.email == credentials.email).first()
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")

        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()

        self._log_audit(user.id, "user_login", "user", str(user.id))
        return self._generate_tokens(user)

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = self.db.query(User).filter(User.id == int(payload["sub"])).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return self._generate_tokens(user)

    def _generate_tokens(self, user: User) -> TokenResponse:
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )

    def _log_audit(self, user_id: int, action: str, resource_type: str, resource_id: str):
        audit = AuditTrail(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
        )
        self.db.add(audit)
        self.db.commit()
