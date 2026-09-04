from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import jwt
from config import Config


def generate_access_token(user: Dict[str, Any], expires_in_hours: int = 24) -> str:
    """Generates a signed JWT access token containing user identity and role claims."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user["id"]),
        "name": user.get("name", ""),
        "email": user["email"],
        "role": user["role"],
        "iat": now,
        "exp": now + timedelta(hours=expires_in_hours)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT access token. Returns payload dict or None if invalid/expired."""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
