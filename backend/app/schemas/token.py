"""Token schemas for AzureShield IAM."""
from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None

class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: str
    exp: int
    iat: int
    type: str = "access"

class TokenData(BaseModel):
    """Token data schema."""
    username: Optional[str] = None

class RefreshToken(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int 