"""OAuth2 and JWT authentication middleware for FastAPI."""
from typing import Optional, List, Annotated
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.requests import Request
from fastapi.responses import Response
import logging
from contextlib import contextmanager

from .jwt_manager import JWTManager, TokenData, UserInfo


logger = logging.getLogger(__name__)

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "analysis:read": "Read analysis results and reports",
        "analysis:write": "Create and modify analysis configurations",
        "analysis:execute": "Execute analysis workflows",
        "system:read": "Read system configuration and status",
        "system:write": "Modify system configuration",
        "admin": "Full administrative access"
    }
)

# HTTP Bearer scheme for API keys
bearer_scheme = HTTPBearer(
    scheme_name="Bearer Token",
    description="JWT Bearer token for API authentication"
)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for JWT token validation."""
    
    def __init__(self, app, jwt_manager: JWTManager, exclude_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.jwt_manager = jwt_manager
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics",
            "/auth/token",
            "/auth/refresh"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request and validate authentication."""
        # Check if path should be excluded from authentication
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            response = await call_next(request)
            return response
        
        # Extract token from Authorization header
        authorization: Optional[str] = request.headers.get("Authorization")
        
        if not authorization:
            return Response(
                content='{"detail": "Authorization header required"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        try:
            scheme, token = authorization.split(" ", 1)
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
        except ValueError:
            return Response(
                content='{"detail": "Invalid authorization header format"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate token
        token_data = self.jwt_manager.verify_token(token)
        if not token_data:
            return Response(
                content='{"detail": "Invalid or expired token"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Add user context to request state
        request.state.user = UserInfo(
            username=token_data.username,
            user_id=token_data.sub,
            scopes=token_data.scopes,
            is_active=True
        )
        request.state.token_data = token_data
        
        # Add security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInfo:
    """Dependency to get current authenticated user from token."""
    from ..api.dependencies import get_jwt_manager
    
    jwt_manager = get_jwt_manager()
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = jwt_manager.verify_token(token)
    if token_data is None:
        raise credentials_exception
    
    user = UserInfo(
        username=token_data.username,
        user_id=token_data.sub,
        scopes=token_data.scopes,
        is_active=True
    )
    
    return user


def get_current_active_user(
    current_user: Annotated[UserInfo, Depends(get_current_user)]
) -> UserInfo:
    """Dependency to get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


class RequireScopes:
    """Dependency class to require specific scopes for endpoints."""
    
    def __init__(self, *required_scopes: str):
        self.required_scopes = set(required_scopes)
    
    def __call__(
        self,
        current_user: Annotated[UserInfo, Depends(get_current_active_user)]
    ) -> UserInfo:
        """Check if user has required scopes."""
        user_scopes = set(current_user.scopes)
        
        # Admin scope grants access to everything
        if "admin" in user_scopes:
            return current_user
        
        # Check if user has all required scopes
        if not self.required_scopes.issubset(user_scopes):
            missing_scopes = self.required_scopes - user_scopes
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Missing scopes: {', '.join(missing_scopes)}"
            )
        
        return current_user


def require_scopes(*scopes: str):
    """Factory function to create scope requirement dependency."""
    return RequireScopes(*scopes)


def get_user_from_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]
) -> UserInfo:
    """Extract user information from bearer token."""
    from ..api.dependencies import get_jwt_manager
    
    jwt_manager = get_jwt_manager()
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = jwt_manager.verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user = UserInfo(
        username=token_data.username,
        user_id=token_data.sub,
        scopes=token_data.scopes,
        is_active=True
    )
    
    return user


@contextmanager
def user_context(user: UserInfo):
    """Context manager for user-specific operations."""
    logger.info(f"Starting operation for user: {user.username}")
    try:
        yield user
    except Exception as e:
        logger.error(f"Operation failed for user {user.username}: {str(e)}")
        raise
    finally:
        logger.info(f"Completed operation for user: {user.username}")


# Common scope requirements
ANALYSIS_READ = require_scopes("analysis:read")
ANALYSIS_WRITE = require_scopes("analysis:write")
ANALYSIS_EXECUTE = require_scopes("analysis:execute")
SYSTEM_READ = require_scopes("system:read")
SYSTEM_WRITE = require_scopes("system:write")
ADMIN_REQUIRED = require_scopes("admin")