from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
import httpx
import json
from ipaddress import ip_address
import geoip2.database
import os

from app.models.user import User, UserSession, UserStatus
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token

class SecurityService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.geoip_reader = None
        if os.path.exists(settings.GEOIP_DATABASE_PATH):
            self.geoip_reader = geoip2.database.Reader(settings.GEOIP_DATABASE_PATH)

    async def check_login_attempts(self, user: User) -> None:
        """Check for suspicious login attempts."""
        # Check if account is locked
        if user.status == UserStatus.LOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is locked. Please reset your password."
            )

        # Check failed login attempts
        if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            user.status = UserStatus.LOCKED
            user.is_active = False
            await self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Too many failed login attempts. Account is locked."
            )

        # Check login attempt timeout
        if user.last_login_attempt:
            timeout = datetime.utcnow() - timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
            if user.last_login_attempt > timeout:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Too many login attempts. Please try again in {settings.ACCOUNT_LOCKOUT_MINUTES} minutes."
                )

    async def check_impossible_travel(
        self, user_id: int, ip_address: str
    ) -> bool:
        """Check for impossible travel between login locations."""
        # Get last successful login session
        query = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        ).order_by(UserSession.last_activity.desc())
        result = await self.db.execute(query)
        last_session = result.scalar_one_or_none()

        if not last_session:
            return False

        # Get location for current IP
        current_location = await self.get_ip_location(ip_address)
        if not current_location:
            return False

        # Get location for last session IP
        last_location = await self.get_ip_location(last_session.ip_address)
        if not last_location:
            return False

        # Calculate distance between locations
        distance = self.calculate_distance(
            current_location["latitude"],
            current_location["longitude"],
            last_location["latitude"],
            last_location["longitude"]
        )

        # Check if distance is suspicious (e.g., > 1000 km in 1 hour)
        time_diff = (datetime.utcnow() - last_session.last_activity).total_seconds() / 3600
        if time_diff < 1 and distance > 1000:  # 1000 km in 1 hour
            return True

        return False

    async def get_ip_location(self, ip: str) -> Optional[Dict[str, Any]]:
        """Get location information for an IP address."""
        try:
            # First try GeoIP database
            if self.geoip_reader:
                response = self.geoip_reader.city(ip)
                return {
                    "latitude": response.location.latitude,
                    "longitude": response.location.longitude,
                    "city": response.city.name,
                    "country": response.country.name,
                    "country_code": response.country.iso_code,
                }

            # Fallback to IP-API
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://ip-api.com/json/{ip}")
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success":
                        return {
                            "latitude": data["lat"],
                            "longitude": data["lon"],
                            "city": data["city"],
                            "country": data["country"],
                            "country_code": data["countryCode"],
                        }

            return None
        except Exception:
            return None

    def calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Calculate distance between two points in kilometers."""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c

        return distance

    async def check_unusual_time(self, user_id: int) -> bool:
        """Check if login time is unusual for the user."""
        # Get user's last 10 successful logins
        query = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        ).order_by(UserSession.last_activity.desc()).limit(10)
        result = await self.db.execute(query)
        sessions = result.scalars().all()

        if not sessions:
            return False

        # Calculate average login hour
        login_hours = [session.last_activity.hour for session in sessions]
        avg_hour = sum(login_hours) / len(login_hours)

        # Check if current hour is significantly different
        current_hour = datetime.utcnow().hour
        hour_diff = abs(current_hour - avg_hour)

        # Consider it unusual if more than 6 hours from average
        return hour_diff > 6

    async def check_device_change(
        self, user_id: int, user_agent: str
    ) -> bool:
        """Check if login device is different from usual."""
        # Get user's last 5 successful logins
        query = select(UserSession).where(
            and_(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
        ).order_by(UserSession.last_activity.desc()).limit(5)
        result = await self.db.execute(query)
        sessions = result.scalars().all()

        if not sessions:
            return False

        # Check if current user agent is significantly different
        for session in sessions:
            if self.compare_user_agents(session.user_agent, user_agent):
                return False

        return True

    def compare_user_agents(self, ua1: str, ua2: str) -> bool:
        """Compare two user agents for similarity."""
        # Extract browser and OS information
        def extract_info(ua: str) -> tuple[str, str]:
            ua = ua.lower()
            browser = "unknown"
            os_name = "unknown"

            if "chrome" in ua:
                browser = "chrome"
            elif "firefox" in ua:
                browser = "firefox"
            elif "safari" in ua:
                browser = "safari"
            elif "edge" in ua:
                browser = "edge"

            if "windows" in ua:
                os_name = "windows"
            elif "macintosh" in ua or "mac os" in ua:
                os_name = "macos"
            elif "linux" in ua:
                os_name = "linux"
            elif "android" in ua:
                os_name = "android"
            elif "iphone" in ua or "ipad" in ua:
                os_name = "ios"

            return browser, os_name

        browser1, os1 = extract_info(ua1)
        browser2, os2 = extract_info(ua2)

        # Consider it similar if either browser or OS matches
        return browser1 == browser2 or os1 == os2

    async def log_security_event(
        self,
        user_id: int,
        event_type: str,
        details: Dict[str, Any],
        severity: str = "info"
    ) -> None:
        """Log a security event."""
        from app.models.audit import AuditLog

        log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            details=json.dumps(details),
            severity=severity,
            ip_address=details.get("ip_address"),
            user_agent=details.get("user_agent"),
        )
        self.db.add(log)
        await self.db.commit() 