from fastapi import Header, HTTPException
from typing import Optional
from .config import Settings

def authorize_tenant(settings: Settings, tenant_id: str, x_api_key: Optional[str]) -> str:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
    expected = settings.api_keys.get(tenant_id)
    if expected is None:
        raise HTTPException(status_code=403, detail="Unknown tenant")
    if x_api_key != expected:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return f"api_key:{x_api_key[-6:]}"
