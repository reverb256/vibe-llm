"""Authentication and API key management for vibe-llm"""
import os
import hashlib
import hmac
from typing import Optional
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
import jwt

security = HTTPBearer()

class AuthManager:
    def __init__(self):
        self.master_key = os.getenv("VIBE_LLM_MASTER_KEY", "your-secure-master-key-here")
        self.jwt_secret = os.getenv("VIBE_LLM_JWT_SECRET", "your-jwt-secret-here")
        self.valid_api_keys = self._load_api_keys()
    
    def _load_api_keys(self) -> dict:
        """Load API keys from environment or config"""
        keys = {}
        
        # Load from environment variables
        for i in range(1, 10):  # Support up to 9 client keys
            key_name = f"VIBE_LLM_CLIENT_KEY_{i}"
            client_name = f"VIBE_LLM_CLIENT_NAME_{i}"
            
            key = os.getenv(key_name)
            name = os.getenv(client_name, f"client_{i}")
            
            if key:
                keys[key] = {
                    "name": name,
                    "created_at": datetime.now(),
                    "permissions": ["chat", "content", "admin"],  # Default permissions
                    "rate_limit": 1000  # requests per hour
                }
        
        # Add master key
        keys[self.master_key] = {
            "name": "master",
            "created_at": datetime.now(),
            "permissions": ["*"],  # All permissions
            "rate_limit": 10000
        }
        
        return keys
    
    def verify_api_key(self, api_key: str) -> Optional[dict]:
        """Verify API key and return client info"""
        if api_key in self.valid_api_keys:
            return self.valid_api_keys[api_key]
        return None
    
    def create_jwt_token(self, client_info: dict, expires_hours: int = 24) -> str:
        """Create JWT token for authenticated client"""
        payload = {
            "client_name": client_info["name"],
            "permissions": client_info["permissions"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=expires_hours),
            "iat": datetime.now(timezone.utc)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    def verify_jwt_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

auth_manager = AuthManager()

async def get_current_client(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Get current authenticated client from API key or JWT token"""
    token = credentials.credentials
    
    # Try as API key first
    client_info = auth_manager.verify_api_key(token)
    if client_info:
        return client_info
    
    # Try as JWT token
    jwt_payload = auth_manager.verify_jwt_token(token)
    if jwt_payload:
        return {
            "name": jwt_payload["client_name"],
            "permissions": jwt_payload["permissions"],
            "rate_limit": 1000  # Default for JWT
        }
    
    raise HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

async def get_admin_client(client: dict = Depends(get_current_client)) -> dict:
    """Require admin permissions"""
    if "*" not in client["permissions"] and "admin" not in client["permissions"]:
        raise HTTPException(
            status_code=403,
            detail="Admin permissions required"
        )
    return client

def check_permission(client: dict, permission: str) -> bool:
    """Check if client has specific permission"""
    return "*" in client["permissions"] or permission in client["permissions"]
