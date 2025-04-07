"""Pydantic schemas for User model."""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID

from app.models.user import UserStatus
from app.schemas.role import Role  # Assuming Role schema is defined elsewhere

class UserBase(BaseModel):
    """Base schema for User."""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: Optional[UserStatus] = None
    email_verified: bool = False
    
    # Pydantic V2 configuration
    model_config = {
        "from_attributes": True
    }

class UserCreate(UserBase):
    """Schema for creating a new user."""
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserUpdate(UserBase):
    """Schema for updating a user."""
    password: Optional[str] = Field(None, min_length=8)

class UserPasswordUpdate(BaseModel):
    """Schema for updating user password."""
    current_password: str
    new_password: str = Field(..., min_length=8)

class UserInDBBase(UserBase):
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Pydantic V2 configuration
    model_config = {
        "from_attributes": True
    }

class UserInDB(UserInDBBase):
    """Schema for User in database."""
    hashed_password: str

class User(UserInDBBase):
    """Schema for User response."""
    roles: List[Role] = []

class UserWithRoles(User):
    """Schema for User with roles."""
    roles: List["Role"] = []

class UserCreateResponse(UserInDBBase):
    message: str = "User created successfully"
    email_verification_token: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    otp_code: Optional[str] = None # Optional OTP code for MFA

class UserLoginResponse(UserInDBBase):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class EmailVerification(BaseModel):
    token: str

class UserSession(BaseModel):
    """Schema for user session."""
    id: int
    user_id: UUID
    session_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    last_activity: Optional[datetime] = None
    is_active: bool

    model_config = {
        "from_attributes": True
    }

class UserSessionCreate(BaseModel):
    user_id: UUID
    session_id: str
    expires_at: datetime

class UserSessionUpdate(BaseModel):
    last_activity: Optional[datetime] = None
    is_active: Optional[bool] = None 