"""API key management and additional security utilities."""

import secrets
from typing import Optional, Dict
from datetime import datetime, timedelta
from config import settings


class APIKeyManager:
    """Manages API keys for additional security layers."""
    
    def __init__(self):
        self._api_keys: Dict[str, Dict] = {}
        # In production, store keys in database or secure storage
        self._load_api_keys()
    
    def _load_api_keys(self) -> None:
        """Load API keys from environment or configuration."""
        # Load from environment variable if set
        api_key = getattr(settings, "api_key", None)
        if api_key:
            self._api_keys[api_key] = {
                "name": "default",
                "created_at": datetime.utcnow(),
                "expires_at": None,
                "active": True,
            }
    
    def generate_api_key(self, name: str = "default", expires_days: Optional[int] = None) -> str:
        """
        Generate a new API key.
        
        Args:
            name: Name/identifier for the key
            expires_days: Optional expiration in days
            
        Returns:
            Generated API key string
        """
        api_key = f"sk_{secrets.token_urlsafe(32)}"
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        self._api_keys[api_key] = {
            "name": name,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "active": True,
        }
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate an API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not api_key:
            return False
        
        key_info = self._api_keys.get(api_key)
        if not key_info:
            return False
        
        if not key_info.get("active", False):
            return False
        
        expires_at = key_info.get("expires_at")
        if expires_at and datetime.utcnow() > expires_at:
            return False
        
        return True
    
    def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            api_key: API key to revoke
            
        Returns:
            True if revoked, False if not found
        """
        if api_key in self._api_keys:
            self._api_keys[api_key]["active"] = False
            return True
        return False
    
    def list_api_keys(self) -> list:
        """
        List all API keys (without exposing full keys).
        
        Returns:
            List of key metadata
        """
        return [
            {
                "name": info["name"],
                "created_at": info["created_at"].isoformat(),
                "expires_at": info["expires_at"].isoformat() if info["expires_at"] else None,
                "active": info["active"],
                "key_prefix": key[:10] + "..." if len(key) > 10 else key,
            }
            for key, info in self._api_keys.items()
        ]


# Global API key manager instance
api_key_manager = APIKeyManager()

