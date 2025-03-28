from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class MFASecret(Base):
    """Model for storing MFA secrets."""
    __tablename__ = "mfa_secrets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    secret = Column(String, nullable=False)
    is_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="mfa_secret")
    backup_codes = relationship("BackupCode", back_populates="mfa_secret", cascade="all, delete-orphan")

class BackupCode(Base):
    """Model for storing MFA backup codes."""
    __tablename__ = "backup_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mfa_secret_id = Column(Integer, ForeignKey("mfa_secrets.id"), nullable=False)
    hashed_code = Column(String, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="backup_codes")
    mfa_secret = relationship("MFASecret", back_populates="backup_codes") 