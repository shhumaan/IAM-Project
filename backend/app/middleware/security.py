from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import time
import json
from datetime import datetime, timedelta
import redis.asyncio as redis
from jose import JWTError, jwt
import ipaddress
import re
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.security import verify_token
from app.core.logging import logger

security = HTTPBearer()

class SecurityMiddleware:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.rate_limit_window = 60  # 1 minute
        self.max_requests_per_window = 100

    async def __call__(
        self,
        request: Request,
        call_next
    ):
        # Get client IP
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # Check IP restrictions
        if not await self.check_ip_restrictions(client_ip):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP address not allowed"
            )

        # Rate limiting
        if not await self.check_rate_limit(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests"
            )

        # JWT validation for protected routes
        if self.is_protected_route(request.url.path):
            try:
                credentials: HTTPAuthorizationCredentials = await security(request)
                token = credentials.credentials
                payload = verify_token(token)
                
                if not payload:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token"
                    )

                # Add user info to request state
                request.state.user = payload
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )

        # Add security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response

    async def check_ip_restrictions(self, ip: str) -> bool:
        """Check if IP is allowed based on restrictions."""
        try:
            ip_addr = ipaddress.ip_address(ip)
            
            # Check against allowed IP ranges
            for allowed_range in settings.ALLOWED_IP_RANGES:
                if ip_addr in ipaddress.ip_network(allowed_range):
                    return True
            
            # Check against blocked IPs
            if ip in settings.BLOCKED_IPS:
                return False
            
            return True
        except ValueError:
            return False

    async def check_rate_limit(self, ip: str) -> bool:
        """Check rate limit for IP address."""
        key = f"rate_limit:{ip}"
        
        # Get current count
        current = await self.redis.get(key)
        if not current:
            # First request in window
            await self.redis.setex(
                key,
                self.rate_limit_window,
                1
            )
            return True
        
        count = int(current)
        if count >= self.max_requests_per_window:
            return False
        
        # Increment counter
        await self.redis.incr(key)
        return True

    def is_protected_route(self, path: str) -> bool:
        """Check if route requires authentication."""
        # List of public routes
        public_routes = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/verify-email",
            "/api/v1/auth/reset-password",
            "/api/v1/oauth/authorize",
            "/api/v1/oauth/callback",
        ]
        
        # Check if path starts with any public route
        return not any(path.startswith(route) for route in public_routes)

    def validate_request_body(self, body: bytes) -> bool:
        """Validate request body for potential security issues."""
        try:
            # Check content type
            if not body:
                return True
            
            # Try to decode as JSON
            try:
                data = json.loads(body)
                # Check for potential XSS in string values
                return not self.contains_xss(data)
            except json.JSONDecodeError:
                # If not JSON, check for potential XSS in raw body
                return not self.contains_xss(body.decode())
        except Exception:
            return False

    def contains_xss(self, data: any) -> bool:
        """Check for potential XSS patterns."""
        if isinstance(data, str):
            # Check for common XSS patterns
            xss_patterns = [
                r"<script>",
                r"javascript:",
                r"onerror=",
                r"onload=",
                r"eval\(",
                r"document\.cookie",
            ]
            return any(re.search(pattern, data, re.IGNORECASE) for pattern in xss_patterns)
        elif isinstance(data, dict):
            return any(self.contains_xss(value) for value in data.values())
        elif isinstance(data, list):
            return any(self.contains_xss(item) for item in data)
        return False

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Add security headers to the response."""
        response = await call_next(request)
        
        # HSTS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content type options
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Frame options
        response.headers["X-Frame-Options"] = "DENY"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self';"
        )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permission Policy
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Log request and response details."""
        start_time = time.time()
        
        # Log request details
        logger.info(
            f"Request started",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "request_id": request.headers.get("X-Request-ID", ""),
            },
        )
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(
            f"Request completed",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
                "request_id": request.headers.get("X-Request-ID", ""),
            },
        )
        
        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware for basic rate limiting.
    
    This is a simple implementation. In production, you'd want to use a more
    robust solution like Redis-based rate limiting.
    """

    def __init__(self, app: ASGIApp, rate_limit: int = 100, window: int = 60) -> None:
        super().__init__(app)
        self.rate_limit = rate_limit  # requests per window
        self.window = window  # window in seconds
        self.ip_requests = {}  # dict to track requests by IP
        
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Apply rate limiting based on client IP."""
        ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries
        self.ip_requests = {
            k: [t for t in v if current_time - t < self.window]
            for k, v in self.ip_requests.items()
        }
        
        # Check if IP has reached rate limit
        if ip in self.ip_requests and len(self.ip_requests[ip]) >= self.rate_limit:
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": str(self.window)},
            )
        
        # Track this request
        if ip not in self.ip_requests:
            self.ip_requests[ip] = []
        self.ip_requests[ip].append(current_time)
        
        # Process the request
        return await call_next(request) 