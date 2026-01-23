"""Authentication middleware for JWT token validation and route protection."""

from typing import Callable
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from api.auth import verify_jwt_token
from core.logging import get_logger

logger = get_logger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic JWT token validation on protected routes.
    
    This middleware can be used to automatically validate tokens for routes
    that require authentication, but it's generally better to use dependencies
    for more fine-grained control.
    """
    
    def __init__(self, app, protected_paths: list[str] = None):
        """
        Initialize authentication middleware.
        
        Args:
            app: FastAPI application instance
            protected_paths: List of path prefixes that require authentication
        """
        super().__init__(app)
        self.protected_paths = protected_paths or ["/api"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and validate authentication for protected paths.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        # Skip authentication for health checks and public endpoints
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Check if path requires authentication
        requires_auth = any(
            request.url.path.startswith(path) for path in self.protected_paths
        )
        
        if requires_auth:
            # Extract token from Authorization header
            authorization = request.headers.get("Authorization")
            
            if not authorization:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": {
                            "message": "Authorization header is required",
                            "type": "AuthenticationError",
                        }
                    }
                )
            
            # Extract token
            try:
                scheme, token = authorization.split()
                if scheme.lower() != "bearer":
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={
                            "error": {
                                "message": "Invalid authorization scheme. Use 'Bearer'",
                                "type": "AuthenticationError",
                            }
                        }
                    )
            except ValueError:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": {
                            "message": "Invalid authorization header format",
                            "type": "AuthenticationError",
                        }
                    }
                )
            
            # Verify token
            payload = verify_jwt_token(token)
            if not payload:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": {
                            "message": "Invalid or expired token",
                            "type": "AuthenticationError",
                        }
                    }
                )
            
            # Add user info to request state for use in route handlers
            request.state.user = {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "metadata": payload.get("user_metadata", {}),
            }
        
        return await call_next(request)

