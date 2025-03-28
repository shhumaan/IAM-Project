"""Security utilities module for AzureShield IAM."""
from datetime import datetime, timedelta
from typing import Any, Optional, Union
from uuid import UUID
from jose import jwt
from passlib.context import CryptContext
from pyotp import TOTP
import hashlib
import hmac

from app.core.config import settings
from app.models.user import User
from app.schemas.token import TokenPayload

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None,
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT refresh token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.JWTError:
        return None

def generate_mfa_secret() -> str:
    """Generate MFA secret."""
    return TOTP.random_base32()

def verify_mfa_code(secret: str, code: str) -> bool:
    """Verify MFA code."""
    totp = TOTP(secret)
    return totp.verify(code)

def generate_audit_log_hash(
    event_type: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str],
    details: Optional[dict],
) -> str:
    """Generate hash for audit log entry."""
    data = {
        "event_type": event_type,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "details": details,
    }
    
    # Sort dictionary to ensure consistent hash
    sorted_data = dict(sorted(data.items()))
    
    # Convert to string and hash
    data_str = str(sorted_data)
    return hmac.new(
        settings.SECRET_KEY.encode(),
        data_str.encode(),
        hashlib.sha256,
    ).hexdigest()

def generate_session_id() -> str:
    """Generate unique session ID."""
    return hashlib.sha256(str(datetime.utcnow().timestamp()).encode()).hexdigest()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = await db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

def generate_password_reset_token(email: str) -> str:
    """Generate a password reset token."""
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "password_reset"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def generate_email_verification_token(email: str) -> str:
    """Generate an email verification token."""
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {
        "exp": expire,
        "sub": email,
        "type": "email_verification"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token and return the email."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except jwt.JWTError:
        return None

def verify_email_verification_token(token: str) -> Optional[str]:
    """Verify an email verification token and return the email."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "email_verification":
            return None
        return payload.get("sub")
    except jwt.JWTError:
        return None 