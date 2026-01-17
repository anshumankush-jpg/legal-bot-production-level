"""
Security Middleware for LegalAI
Implements rate limiting, security headers, and bot protection
"""
import logging
import time
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """
    Simple in-memory rate limiter.
    Production: Use Redis for distributed rate limiting.
    """
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.limits = {
            '/api/auth/session': (10, 60),       # 10 requests per minute
            '/api/auth/register': (5, 60),       # 5 requests per minute
            '/api/uploads/signed-url': (30, 60), # 30 requests per minute
            'default': (100, 60)                 # 100 requests per minute default
        }
    
    def is_allowed(self, key: str, path: str) -> tuple[bool, Optional[str]]:
        """
        Check if request is allowed.
        
        Args:
            key: Client identifier (IP address)
            path: Request path
            
        Returns:
            (allowed, error_message)
        """
        now = time.time()
        
        # Get limit for this endpoint
        limit, window = self.limits.get(path, self.limits['default'])
        
        # Get request history for this key+path
        request_key = f"{key}:{path}"
        request_times = self.requests[request_key]
        
        # Remove old requests outside window
        cutoff = now - window
        self.requests[request_key] = [t for t in request_times if t > cutoff]
        
        # Check if under limit
        if len(self.requests[request_key]) >= limit:
            retry_after = int(self.requests[request_key][0] + window - now)
            return False, f"Rate limit exceeded. Try again in {retry_after} seconds."
        
        # Record this request
        self.requests[request_key].append(now)
        
        return True, None
    
    def cleanup_old_entries(self):
        """Periodic cleanup of old request records"""
        now = time.time()
        for key in list(self.requests.keys()):
            self.requests[key] = [t for t in self.requests[key] if t > now - 3600]
            if not self.requests[key]:
                del self.requests[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


# ============================================================================
# RATE LIMITING MIDDLEWARE
# ============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting"""
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        allowed, error_msg = rate_limiter.is_allowed(client_ip, request.url.path)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_ip} on {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": error_msg},
                headers={"Retry-After": "60"}
            )
        
        response = await call_next(request)
        return response


# ============================================================================
# SECURITY HEADERS MIDDLEWARE
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Determine if production
        is_prod = os.getenv('ENVIRONMENT', 'dev') == 'prod'
        
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com https://apis.google.com",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https: blob:",
            "font-src 'self' data:",
            "connect-src 'self' https://firebaseapp.com https://*.googleapis.com https://identitytoolkit.googleapis.com",
            "frame-src 'self' https://accounts.google.com https://login.microsoftonline.com",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Other security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS in production only
        if is_prod:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response


# ============================================================================
# CORS CONFIGURATION
# ============================================================================

def get_cors_origins() -> list:
    """Get allowed CORS origins based on environment"""
    env = os.getenv('ENVIRONMENT', 'dev')
    
    if env == 'dev':
        return [
            "http://localhost:4200",
            "http://localhost:4201",
            "http://localhost:5173",
            "http://127.0.0.1:4200"
        ]
    elif env == 'staging':
        return [
            "https://dev.legalai.work",
            "https://staging.legalai.work"
        ]
    else:  # prod
        return [
            "https://legalai.work",
            "https://www.legalai.work"
        ]


# ============================================================================
# BOT PROTECTION (Placeholder for reCAPTCHA/Turnstile)
# ============================================================================

class BotProtectionMiddleware(BaseHTTPMiddleware):
    """
    Bot protection middleware (placeholder).
    
    In production, integrate reCAPTCHA or Cloudflare Turnstile:
    - Check captcha token on sensitive endpoints
    - Block requests with suspicious patterns
    - Implement challenge-response for high-risk actions
    """
    
    async def dispatch(self, request: Request, call_next):
        # TODO: Implement reCAPTCHA verification
        # For now, just pass through
        
        # Example implementation:
        # if request.url.path in ['/api/auth/session', '/api/auth/register']:
        #     captcha_token = request.headers.get('X-Captcha-Token')
        #     if not await verify_recaptcha(captcha_token):
        #         return JSONResponse(
        #             status_code=400,
        #             content={"detail": "Captcha verification failed"}
        #         )
        
        response = await call_next(request)
        return response


import os  # Add import
