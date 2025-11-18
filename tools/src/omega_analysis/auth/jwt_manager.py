"""JWT token models and utilities for authentication."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets


class TokenData(BaseModel):
    """Token data model for JWT tokens."""
    username: Optional[str] = None
    scopes: list[str] = Field(default_factory=list)
    sub: Optional[str] = None
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
    jti: Optional[str] = None


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class UserInfo(BaseModel):
    """User information model."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    scopes: list[str] = Field(default_factory=list)
    user_id: Optional[str] = None


class JWTManager:
    """JWT token manager for creating and validating tokens."""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32)
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new refresh token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            username: str = payload.get("sub")
            scopes: list[str] = payload.get("scopes", [])
            exp: Optional[datetime] = None
            iat: Optional[datetime] = None
            jti: Optional[str] = payload.get("jti")
            
            if payload.get("exp"):
                exp = datetime.fromtimestamp(payload["exp"])
            
            if payload.get("iat"):
                iat = datetime.fromtimestamp(payload["iat"])
            
            if username is None:
                return None
            
            token_data = TokenData(
                username=username,
                scopes=scopes,
                sub=username,
                exp=exp,
                iat=iat,
                jti=jti
            )
            
            return token_data
            
        except JWTError:
            return None
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)
    
    def create_token_pair(self, user_data: Dict[str, Any]) -> Token:
        """Create both access and refresh tokens."""
        access_token = self.create_access_token(data=user_data)
        refresh_token = self.create_refresh_token(data=user_data)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.access_token_expire_minutes * 60,
            refresh_token=refresh_token,
            scope=" ".join(user_data.get("scopes", []))
        )