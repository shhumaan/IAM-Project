from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List

from app.api.dependencies import get_current_user, get_db
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
    Enroll user in MFA.
    Returns secret, QR code, and backup codes.
    """
    mfa_service = MFAService(db)
    
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
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
    Verify MFA code and enable MFA for user.
    """
    mfa_service = MFAService(db)
    
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    is_valid = await mfa_service.verify_mfa(
        current_user.id,
        request.code,
        request.secret
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    await mfa_service.enable_mfa(current_user.id)
    
    return MFAVerifyResponse(
        enabled=True,
        message="MFA enabled successfully"
    )

@router.post("/verify-backup", response_model=MFAVerifyResponse)
async def verify_backup_code(
    request: BackupCodeVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify backup code and enable MFA for user.
    """
    mfa_service = MFAService(db)
    
    is_valid = await mfa_service.verify_backup_code(
        current_user.id,
        request.code
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid backup code"
        )
    
    return MFAVerifyResponse(
        enabled=True,
        message="Backup code verified successfully"
    )

@router.get("/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get MFA status for current user.
    """
    return MFAStatusResponse(
        enabled=current_user.mfa_enabled,
        methods=["totp"] if current_user.mfa_enabled else []
    )

@router.post("/disable")
async def disable_mfa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disable MFA for current user.
    """
    mfa_service = MFAService(db)
    
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    await mfa_service.disable_mfa(current_user.id)
    
    return {"message": "MFA disabled successfully"} 