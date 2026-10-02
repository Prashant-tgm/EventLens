"""
Password hashing (bcrypt) and JWT token creation / verification.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def generate_download_token(event_id: str, photo_id: int) -> str:
    """Create a short-lived HMAC token for secure photo downloads."""
    import hashlib
    import hmac
    import time
    timestamp = int(time.time())
    message = f"{event_id}:{photo_id}:{timestamp}"
    signature = hmac.new(
        settings.DOWNLOAD_TOKEN_SECRET.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{timestamp}:{signature}"


def verify_download_token(
    event_id: str, photo_id: int, token: str,
) -> bool:
    """Verify an HMAC download token is valid and not expired."""
    import hashlib
    import hmac
    import time
    try:
        parts = token.split(":")
        if len(parts) != 2:
            return False
        timestamp_str, signature = parts
        timestamp = int(timestamp_str)
        # Check expiry
        if time.time() - timestamp > settings.DOWNLOAD_TOKEN_EXPIRY:
            return False
        # Verify HMAC
        message = f"{event_id}:{photo_id}:{timestamp}"
        expected = hmac.new(
            settings.DOWNLOAD_TOKEN_SECRET.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(signature, expected)
    except (ValueError, TypeError):
        return False

