import pyotp
import qrcode
import io
import base64
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, MFASecret, BackupCode
from app.core.security import get_password_hash
from app.core.config import settings

class MFAService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def generate_totp_secret(self) -> str:
        """Generate a new TOTP secret."""
        return pyotp.random_base32()

    def generate_qr_code(self, secret: str, email: str) -> str:
        """Generate QR code for authenticator app."""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=email,
            issuer_name=settings.PROJECT_NAME
        )
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def generate_backup_codes(self) -> List[str]:
        """Generate backup codes for MFA recovery."""
        codes = []
        for _ in range(8):  # Generate 8 backup codes
            code = secrets.token_urlsafe(8)
            codes.append(code)
        return codes

    async def enroll_mfa(self, user_id: int) -> Tuple[str, str, List[str]]:
        """Enroll a user in MFA."""
        # Check if user already has MFA enabled
        query = select(MFASecret).where(MFASecret.user_id == user_id)
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is already enabled for this user"
            )

        # Generate new TOTP secret
        secret = self.generate_totp_secret()
        
        # Get user email for QR code
        user_query = select(User).where(User.id == user_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Generate QR code
        qr_code = self.generate_qr_code(secret, user.email)
        
        # Generate backup codes
        backup_codes = self.generate_backup_codes()
        
        # Store MFA secret and backup codes
        mfa_secret = MFASecret(
            user_id=user_id,
            secret=secret,
            is_enabled=False,  # Will be enabled after verification
            created_at=datetime.utcnow()
        )
        self.db.add(mfa_secret)
        
        # Store hashed backup codes
        for code in backup_codes:
            backup_code = BackupCode(
                user_id=user_id,
                hashed_code=get_password_hash(code),
                is_used=False,
                created_at=datetime.utcnow()
            )
            self.db.add(backup_code)
        
        await self.db.commit()
        return secret, qr_code, backup_codes

    async def verify_mfa(self, user_id: int, token: str) -> bool:
        """Verify MFA token."""
        query = select(MFASecret).where(MFASecret.user_id == user_id)
        result = await self.db.execute(query)
        mfa_secret = result.scalar_one_or_none()
        
        if not mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not enabled for this user"
            )

        totp = pyotp.TOTP(mfa_secret.secret)
        is_valid = totp.verify(token)
        
        if is_valid and not mfa_secret.is_enabled:
            # First successful verification - enable MFA
            mfa_secret.is_enabled = True
            mfa_secret.verified_at = datetime.utcnow()
            await self.db.commit()
        
        return is_valid

    async def verify_backup_code(self, user_id: int, code: str) -> bool:
        """Verify backup code."""
        query = select(BackupCode).where(
            BackupCode.user_id == user_id,
            BackupCode.is_used == False
        )
        result = await self.db.execute(query)
        backup_codes = result.scalars().all()
        
        for backup_code in backup_codes:
            if verify_password(code, backup_code.hashed_code):
                backup_code.is_used = True
                backup_code.used_at = datetime.utcnow()
                await self.db.commit()
                return True
        
        return False

    async def disable_mfa(self, user_id: int) -> None:
        """Disable MFA for a user."""
        # Delete MFA secret
        mfa_query = select(MFASecret).where(MFASecret.user_id == user_id)
        mfa_result = await self.db.execute(mfa_query)
        mfa_secret = mfa_result.scalar_one_or_none()
        
        if mfa_secret:
            await self.db.delete(mfa_secret)
        
        # Delete backup codes
        backup_query = select(BackupCode).where(BackupCode.user_id == user_id)
        backup_result = await self.db.execute(backup_query)
        backup_codes = backup_result.scalars().all()
        
        for backup_code in backup_codes:
            await self.db.delete(backup_code)
        
        await self.db.commit()

    async def get_mfa_status(self, user_id: int) -> dict:
        """Get MFA status for a user."""
        query = select(MFASecret).where(MFASecret.user_id == user_id)
        result = await self.db.execute(query)
        mfa_secret = result.scalar_one_or_none()
        
        if not mfa_secret:
            return {
                "is_enabled": False,
                "enrolled_at": None,
                "verified_at": None
            }
        
        return {
            "is_enabled": mfa_secret.is_enabled,
            "enrolled_at": mfa_secret.created_at,
            "verified_at": mfa_secret.verified_at
        }

    async def get_remaining_backup_codes(self, user_id: int) -> int:
        """Get count of remaining backup codes."""
        query = select(BackupCode).where(
            BackupCode.user_id == user_id,
            BackupCode.is_used == False
        )
        result = await self.db.execute(query)
        return len(result.scalars().all()) 