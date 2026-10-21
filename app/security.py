from fastapi import Header, HTTPException
from app.config import settings

def get_current_user(x_dev_user: str | None = Header(default=None, alias="X-Dev-User")) -> str:
    """Local development stub ONLY. Replace with trusted LDAP/SSO before shared use."""
    if not settings.allow_dev_identity:
        raise HTTPException(status_code=501, detail="LDAP/SSO integration is not configured")
    if not x_dev_user or not x_dev_user.strip():
        raise HTTPException(status_code=401, detail="X-Dev-User is required for local development only")
    return x_dev_user.strip()
