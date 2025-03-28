from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    generate_password_reset_token,
    generate_email_verification_token,
)
from app.models.user import User, UserSession, UserStatus
from app.schemas.user import (
    UserCreate,
    UserLogin,
    PasswordReset,
    PasswordResetConfirm,
    EmailVerification,
    UserSessionCreate,
)
from app.core.config import settings

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_in: UserCreate) -> User:
        # Check if user already exists
        query = select(User).where(User.email == user_in.email)
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            status=UserStatus.PENDING,
            email_verification_token=generate_email_verification_token(user_in.email),
            email_verification_expires=datetime.utcnow() + timedelta(hours=24),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate_user(self, user_in: UserLogin) -> Optional[User]:
        query = select(User).where(User.email == user_in.email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not verify_password(user_in.password, user.hashed_password):
            return None
            
        return user

    async def login_user(
        self, user: User, ip_address: str, user_agent: str
    ) -> tuple[str, str, UserSession]:
        # Check if user is locked
        if user.status == UserStatus.LOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked. Please reset your password.",
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        # Check if email is verified
        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not verified",
            )

        # Create tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Create session
        session = UserSession(
            user_id=user.id,
            session_id=str(uuid.uuid4()),
            access_token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        # Update user login info
        user.last_login = datetime.utcnow()
        user.failed_login_attempts = 0
        await self.db.commit()

        return access_token, refresh_token, session

    async def logout_user(self, session_id: str) -> None:
        query = select(UserSession).where(UserSession.session_id == session_id)
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if session:
            session.is_active = False
            await self.db.commit()

    async def refresh_token(self, refresh_token: str) -> tuple[str, str]:
        # Verify refresh token
        query = select(UserSession).where(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow(),
        )
        result = await self.db.execute(query)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Create new tokens
        new_access_token = create_access_token(session.user_id)
        new_refresh_token = create_refresh_token(session.user_id)

        # Update session
        session.access_token = new_access_token
        session.refresh_token = new_refresh_token
        session.last_activity = datetime.utcnow()
        await self.db.commit()

        return new_access_token, new_refresh_token

    async def request_password_reset(self, email: str) -> None:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            user.password_reset_token = generate_password_reset_token(email)
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
            await self.db.commit()

    async def reset_password(self, token: str, new_password: str) -> None:
        query = select(User).where(
            User.password_reset_token == token,
            User.password_reset_expires > datetime.utcnow(),
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token",
            )

        user.hashed_password = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.last_password_change = datetime.utcnow()
        await self.db.commit()

    async def verify_email(self, token: str) -> None:
        query = select(User).where(
            User.email_verification_token == token,
            User.email_verification_expires > datetime.utcnow(),
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired email verification token",
            )

        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        user.status = UserStatus.ACTIVE
        await self.db.commit()

    async def handle_failed_login(self, user: User) -> None:
        user.failed_login_attempts += 1
        user.last_login_attempt = datetime.utcnow()

        if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            user.status = UserStatus.LOCKED
            user.is_active = False

        await self.db.commit() 