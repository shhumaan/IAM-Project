"""Pydantic schemas for User model."""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr, Field
from datetime import datetime
from uuid import UUID

from app.models.user import UserStatus

class UserBase(BaseModel):
    """Base schema for User."""
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)

class UserInDB(UserBase):
    """Schema for User in database."""
    id: UUID
    mfa_enabled: bool
    mfa_secret: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class User(UserInDB):
    """Schema for User response."""
    pass

class UserWithRoles(User):
    """Schema for User with roles."""
    roles: List["Role"] = []

class UserInDBBase(UserBase):
    id: Optional[int] = None
    status: Optional[UserStatus] = None
    email_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserCreateResponse(UserInDBBase):
    message: str = "User created successfully"
    email_verification_token: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse(UserInDBBase):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: constr(min_length=8)

class EmailVerification(BaseModel):
    token: str

class UserSession(BaseModel):
    """Schema for user session."""
    id: int
    user_id: UUID
    session_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    last_activity: Optional[datetime] = None
    is_active: bool

    class Config:
        """Pydantic config."""
        from_attributes = True

class UserSessionCreate(BaseModel):
    ip_address: str
    user_agent: str
    expires_at: datetime

class UserSessionUpdate(BaseModel):
    last_activity: datetime
    is_active: bool 