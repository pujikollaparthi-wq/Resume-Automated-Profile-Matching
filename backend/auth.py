import jwt
import datetime
from typing import Optional, Dict, Any
from fastapi import HTTPException, Header, Depends
from backend.database import get_db, hash_password

SECRET_KEY = "ai-profile-matcher-jwt-secret-key-2026-super-secure"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(hours=24))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Extract current user from Bearer token if present."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        return None
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, full_name, role FROM users WHERE username = ?", (payload["sub"],))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return dict(user)
    return None

def require_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Require authenticated user."""
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication token required or expired.")
    return user

def require_admin_or_recruiter(user: Dict[str, Any] = Depends(require_current_user)) -> Dict[str, Any]:
    """Require recruiter or admin privileges."""
    if user.get("role") not in ["admin", "recruiter"]:
        raise HTTPException(status_code=403, detail="Recruiter or Admin access required.")
    return user
