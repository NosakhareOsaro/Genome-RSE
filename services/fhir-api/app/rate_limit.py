"""Rate limiting via slowapi.

A default per-client (keyed by remote address) limit is applied to
every route through `Limiter(default_limits=...)` + `SlowAPIMiddleware`
in app/main.py, rather than decorating each endpoint individually.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings

limiter = Limiter(key_func=get_remote_address, default_limits=[get_settings().rate_limit])
