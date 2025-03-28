from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.models.user import User
from app.schemas.mfa import (
    MFAEnrollResponse,
    MFAVerifyRequest,
    MFAVerifyResponse,
    BackupCodeVerifyRequest,
    MFAStatusResponse,
)
from app.services.mfa import MFAService

router = APIRouter()

@router.post("/enroll", response_model=MFAEnrollResponse)
async def enroll_mfa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Enroll a user in MFA.
    This endpoint generates a TOTP secret, QR code, and backup codes.
    The user must verify the TOTP token before MFA is enabled.
    """
    mfa_service = MFAService(db)
    secret, qr_code, backup_codes = await mfa_service.enroll_mfa(current_user.id)
    
    return MFAEnrollResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )

@router.post("/verify", response_model=MFAVerifyResponse)
async def verify_mfa(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a TOTP token for MFA.
    On first successful verification, MFA is enabled for the user.
    """
    mfa_service = MFAService(db)
    is_valid = await mfa_service.verify_mfa(current_user.id, request.token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA token"
        )
    
    return MFAVerifyResponse(
        is_valid=True,
        mfa_enabled=True
    )

@router.post("/verify-backup", response_model=MFAVerifyResponse)
async def verify_backup_code(
    request: BackupCodeVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a backup code for MFA recovery.
    Backup codes are single-use and are marked as used after verification.
    """
    mfa_service = MFAService(db)
    is_valid = await mfa_service.verify_backup_code(current_user.id, request.code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid backup code"
        )
    
    return MFAVerifyResponse(
        is_valid=True,
        mfa_enabled=True
    )

@router.post("/disable")
async def disable_mfa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disable MFA for a user.
    This endpoint deletes the MFA secret and all backup codes.
    """
    mfa_service = MFAService(db)
    await mfa_service.disable_mfa(current_user.id)
    
    return {"message": "MFA disabled successfully"}

@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current MFA status for a user.
    Returns whether MFA is enabled, enrollment date, verification date,
    and number of remaining backup codes.
    """
    mfa_service = MFAService(db)
    status = await mfa_service.get_mfa_status(current_user.id)
    remaining_codes = await mfa_service.get_remaining_backup_codes(current_user.id)
    
    return MFAStatusResponse(
        **status,
        remaining_backup_codes=remaining_codes
    ) 