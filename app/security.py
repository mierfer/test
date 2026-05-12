"""Security protections: rate limiting, security headers, login brute-force defense."""
import time
import functools
import threading
from collections import defaultdict
from flask import request, jsonify


# ----- Rate limiter (in-memory, per-IP) -----

_lock = threading.Lock()
_window: dict[str, list[float]] = defaultdict(list)


def _clean_window(key: str, seconds: int, now: float) -> None:
    cutoff = now - seconds
    _window[key] = [t for t in _window[key] if t > cutoff]


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """Decorator: limit a route to *max_requests* per *window_seconds* per IP."""

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            key = f"rl:{request.blueprint}:{f.__name__}:{request.remote_addr}"
            now = time.time()
            with _lock:
                _clean_window(key, window_seconds, now)
                if len(_window[key]) >= max_requests:
                    retry_after = int(_window[key][0] + window_seconds - now + 1)
                    return (
                        jsonify(
                            {
                                "error": "请求过于频繁，请稍后再试",
                                "retry_after": retry_after,
                            }
                        ),
                        429,
                        {"Retry-After": str(retry_after)},
                    )
                _window[key].append(now)
            return f(*args, **kwargs)

        return wrapper

    return decorator


def login_rate_limit(f):
    """Stricter rate limit for login: 5 attempts per 3 minutes per IP."""
    return rate_limit(max_requests=5, window_seconds=180)(f)


# ----- Security headers -----

_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


def init_security(app):
    """Inject security headers on every HTML response."""

    @app.after_request
    def _add_security_headers(response):
        for header, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)

        # Only cache-bust HTML pages, let static assets use browser cache
        ct = response.content_type or ""
        if "text/html" in ct:
            response.headers.setdefault("Cache-Control", "no-store, max-age=0")

        return response
