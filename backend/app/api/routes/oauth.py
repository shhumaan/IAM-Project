from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.models.user import User
from app.schemas.oauth import (
    OAuthAuthorizeRequest,
    OAuthAuthorizeResponse,
    OAuthCallbackRequest,
    OAuthLoginResponse,
    OAuthLinkRequest,
    OAuthUnlinkRequest,
    OAuthProviderInfo,
)
from app.services.oauth import OAuthService

router = APIRouter()

@router.get("/providers", response_model=list[OAuthProviderInfo])
async def list_oauth_providers():
    """
    List available OAuth providers and their configuration.
    """
    providers = [
        OAuthProviderInfo(
            name="google",
            display_name="Google",
            enabled=True,
            scopes=["openid", "email", "profile"]
        ),
        OAuthProviderInfo(
            name="github",
            display_name="GitHub",
            enabled=True,
            scopes=["user:email"]
        ),
    ]
    return providers

@router.post("/authorize", response_model=OAuthAuthorizeResponse)
async def authorize_oauth(
    request: OAuthAuthorizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Start OAuth2 authorization flow.
    Returns the authorization URL and PKCE parameters.
    """
    oauth_service = OAuthService(db)
    auth_url, code_verifier = oauth_service.get_authorization_url(
        request.provider,
        request.redirect_uri
    )
    
    return OAuthAuthorizeResponse(
        authorization_url=auth_url,
        state=secrets.token_urlsafe(32),
        code_verifier=code_verifier
    )

@router.post("/callback", response_model=OAuthLoginResponse)
async def oauth_callback(
    request: OAuthCallbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle OAuth2 callback.
    Exchanges the authorization code for tokens and creates/updates user.
    """
    oauth_service = OAuthService(db)
    
    # Get access token
    token_response = await oauth_service.get_access_token(
        request.provider,
        request.code,
        request.redirect_uri,
        request.code_verifier
    )
    
    # Get user info
    user_info = await oauth_service.get_user_info(
        request.provider,
        token_response["access_token"]
    )
    
    # Handle login
    user, access_token, refresh_token = await oauth_service.handle_oauth_login(
        request.provider,
        user_info
    )
    
    return OAuthLoginResponse(
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
        },
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/link")
async def link_oauth_account(
    request: OAuthLinkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Link an OAuth account to the current user.
    """
    oauth_service = OAuthService(db)
    
    # Get access token
    token_response = await oauth_service.get_access_token(
        request.provider,
        request.code,
        request.redirect_uri,
        request.code_verifier
    )
    
    # Get user info
    user_info = await oauth_service.get_user_info(
        request.provider,
        token_response["access_token"]
    )
    
    # Link account
    await oauth_service.link_oauth_account(
        current_user.id,
        request.provider,
        user_info
    )
    
    return {"message": f"Successfully linked {request.provider} account"}

@router.post("/unlink")
async def unlink_oauth_account(
    request: OAuthUnlinkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Unlink an OAuth account from the current user.
    """
    oauth_service = OAuthService(db)
    await oauth_service.unlink_oauth_account(
        current_user.id,
        request.provider
    )
    
    return {"message": f"Successfully unlinked {request.provider} account"} 