from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class OAuthAuthorizeRequest(BaseModel):
    """Request schema for OAuth authorization."""
    provider: str = Field(..., description="OAuth provider (e.g., 'google', 'github')")
    redirect_uri: str = Field(..., description="Redirect URI after authorization")

class OAuthAuthorizeResponse(BaseModel):
    """Response schema for OAuth authorization."""
    authorization_url: str = Field(..., description="URL to redirect user to for authorization")
    state: str = Field(..., description="State parameter for CSRF protection")
    code_verifier: str = Field(..., description="PKCE code verifier")

class OAuthCallbackRequest(BaseModel):
    """Request schema for OAuth callback."""
    code: str = Field(..., description="Authorization code from OAuth provider")
    state: str = Field(..., description="State parameter for CSRF protection")
    code_verifier: str = Field(..., description="PKCE code verifier")

class OAuthTokenResponse(BaseModel):
    """Response schema for OAuth token exchange."""
    access_token: str = Field(..., description="OAuth access token")
    token_type: str = Field(..., description="Token type (usually 'Bearer')")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token")
    scope: Optional[str] = Field(None, description="Token scope")
    id_token: Optional[str] = Field(None, description="OpenID Connect ID token")

class OAuthUserInfo(BaseModel):
    """Schema for OAuth user information."""
    sub: str = Field(..., description="Unique identifier from OAuth provider")
    email: str = Field(..., description="User's email address")
    name: Optional[str] = Field(None, description="User's full name")
    picture: Optional[str] = Field(None, description="URL to user's profile picture")
    provider: str = Field(..., description="OAuth provider name")
    provider_data: Dict[str, Any] = Field(..., description="Raw provider data")

class OAuthLoginResponse(BaseModel):
    """Response schema for OAuth login."""
    user: Dict[str, Any] = Field(..., description="User information")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")

class OAuthLinkRequest(BaseModel):
    """Request schema for linking OAuth account."""
    provider: str = Field(..., description="OAuth provider to link")
    code: str = Field(..., description="Authorization code from OAuth provider")
    state: str = Field(..., description="State parameter for CSRF protection")
    code_verifier: str = Field(..., description="PKCE code verifier")

class OAuthUnlinkRequest(BaseModel):
    """Request schema for unlinking OAuth account."""
    provider: str = Field(..., description="OAuth provider to unlink")

class OAuthProviderInfo(BaseModel):
    """Schema for OAuth provider information."""
    name: str = Field(..., description="Provider name")
    display_name: str = Field(..., description="Human-readable provider name")
    enabled: bool = Field(..., description="Whether the provider is enabled")
    scopes: list[str] = Field(..., description="Required OAuth scopes") 