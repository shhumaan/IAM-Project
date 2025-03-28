from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
from jose import jwt
import secrets
import hashlib
import base64

from app.models.user import User, UserStatus
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token

class OAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.providers = {
            "google": {
                "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "scopes": ["openid", "email", "profile"],
            },
            "github": {
                "authorize_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "scopes": ["user:email"],
            },
        }

    def generate_pkce(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge."""
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        return code_verifier, code_challenge

    def get_authorization_url(self, provider: str, redirect_uri: str) -> tuple[str, str]:
        """Get OAuth2 authorization URL with PKCE."""
        if provider not in self.providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )

        provider_config = self.providers[provider]
        code_verifier, code_challenge = self.generate_pkce()

        params = {
            "client_id": provider_config["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(provider_config["scopes"]),
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": secrets.token_urlsafe(32),
        }

        auth_url = f"{provider_config['authorize_url']}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        return auth_url, code_verifier

    async def get_access_token(
        self, provider: str, code: str, redirect_uri: str, code_verifier: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        if provider not in self.providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )

        provider_config = self.providers[provider]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                provider_config["token_url"],
                data={
                    "client_id": provider_config["client_id"],
                    "client_secret": provider_config["client_secret"],
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "code_verifier": code_verifier,
                    "grant_type": "authorization_code",
                },
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get access token"
                )
            
            return response.json()

    async def get_user_info(self, provider: str, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider."""
        if provider not in self.providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported OAuth provider: {provider}"
            )

        provider_config = self.providers[provider]
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(
                provider_config["userinfo_url"],
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info"
                )
            
            return response.json()

    async def handle_oauth_login(
        self, provider: str, user_info: Dict[str, Any]
    ) -> tuple[User, str, str]:
        """Handle OAuth login and create/update user."""
        email = user_info.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by OAuth provider"
            )

        # Check if user exists
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            # Create new user
            user = User(
                email=email,
                full_name=user_info.get("name", ""),
                is_active=True,
                status=UserStatus.ACTIVE,
                email_verified=True,  # Email is verified by OAuth provider
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

        # Create tokens
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return user, access_token, refresh_token

    async def link_oauth_account(
        self, user_id: int, provider: str, user_info: Dict[str, Any]
    ) -> None:
        """Link OAuth account to existing user."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Store OAuth provider info
        # This could be extended to store provider-specific data
        user.external_id = user_info.get("sub")
        user.external_provider = provider
        await self.db.commit()

    async def unlink_oauth_account(self, user_id: int, provider: str) -> None:
        """Unlink OAuth account from user."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.external_provider != provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Account not linked to {provider}"
            )

        user.external_id = None
        user.external_provider = None
        await self.db.commit() 