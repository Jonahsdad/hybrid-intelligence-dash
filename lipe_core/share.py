from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from uuid import uuid4

@dataclass
class _ShareItem:
    payload: Dict[str, Any]
    expire_at: datetime

_STORE: Dict[str, _ShareItem] = {}

def share_create(body):
    token = uuid4().hex
    ttl = getattr(body, "ttl_hours", 24) or 24
    _STORE[token] = _ShareItem(payload=body.dict(), expire_at=datetime.now(timezone.utc)+timedelta(hours=ttl))
    return {"token": token, "url": f"/v1/share/{token}", "expires_in_hours": ttl}

def share_get(token: str) -> Optional[Dict[str, Any]]:
    item = _STORE.get(token)
    if not item: return None
    if item.expire_at < datetime.now(timezone.utc):
        _STORE.pop(token, None); return None
    return item.payload
