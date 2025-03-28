from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MFAEnrollResponse(BaseModel):
    """Response schema for MFA enrollment."""
    secret: str = Field(..., description="TOTP secret for manual entry")
    qr_code: str = Field(..., description="Base64 encoded QR code for authenticator app")
    backup_codes: List[str] = Field(..., description="List of backup codes for recovery")

class MFAVerifyRequest(BaseModel):
    """Request schema for MFA verification."""
    token: str = Field(..., description="6-digit TOTP token", min_length=6, max_length=6)

class MFAVerifyResponse(BaseModel):
    """Response schema for MFA verification."""
    is_valid: bool = Field(..., description="Whether the token is valid")
    mfa_enabled: bool = Field(..., description="Whether MFA is now enabled")

class BackupCodeVerifyRequest(BaseModel):
    """Request schema for backup code verification."""
    code: str = Field(..., description="Backup code for recovery")

class MFAStatusResponse(BaseModel):
    """Response schema for MFA status."""
    is_enabled: bool = Field(..., description="Whether MFA is enabled")
    enrolled_at: Optional[datetime] = Field(None, description="When MFA was enrolled")
    verified_at: Optional[datetime] = Field(None, description="When MFA was verified")
    remaining_backup_codes: int = Field(..., description="Number of remaining backup codes")

class MFASecretBase(BaseModel):
    """Base schema for MFA secret."""
    user_id: int
    secret: str
    is_enabled: bool = False
    created_at: datetime
    verified_at: Optional[datetime] = None

class MFASecretCreate(MFASecretBase):
    """Schema for creating MFA secret."""
    pass

class MFASecret(MFASecretBase):
    """Schema for MFA secret."""
    id: int

    class Config:
        from_attributes = True

class BackupCodeBase(BaseModel):
    """Base schema for backup code."""
    user_id: int
    hashed_code: str
    is_used: bool = False
    created_at: datetime
    used_at: Optional[datetime] = None

class BackupCodeCreate(BackupCodeBase):
    """Schema for creating backup code."""
    pass

class BackupCode(BackupCodeBase):
    """Schema for backup code."""
    id: int

    class Config:
        from_attributes = True 