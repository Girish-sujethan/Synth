"""Supabase authentication utilities for JWT token validation and user extraction."""

from typing import Optional, Dict, Any
from supabase import create_client, Client
import requests
from config import settings
from core.logging import get_logger

logger = get_logger(__name__)

# Supabase client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance.
    
    Returns:
        Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        if not settings.supabase_url:
            raise ValueError("SUPABASE_URL is not configured")
        
        supabase_key = settings.supabase_key or ""
        _supabase_client = create_client(settings.supabase_url, supabase_key)
    
    return _supabase_client


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token using Supabase.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        # Create a temporary Supabase client with the token
        # The client will verify the token when we call get_user
        supabase = get_supabase_client()
        
        # Use the token to get user info (Supabase verifies internally)
        # Note: This approach uses Supabase's built-in verification
        try:
            # Set session with the provided token
            # The refresh token is not needed for verification
            user_response = supabase.auth.get_user(token)
            
            if user_response and user_response.user:
                return {
                    "sub": user_response.user.id,
                    "email": user_response.user.email,
                    "user_metadata": user_response.user.user_metadata or {},
                    "app_metadata": user_response.user.app_metadata or {},
                }
        except AttributeError:
            # Fallback: try direct API call to verify token
            # Supabase REST API endpoint for user info
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": settings.supabase_key or "",
            }
            response = requests.get(
                f"{settings.supabase_url}/auth/v1/user",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "sub": user_data.get("id"),
                    "email": user_data.get("email"),
                    "user_metadata": user_data.get("user_metadata", {}),
                    "app_metadata": user_data.get("app_metadata", {}),
                }
        
        return None
        
    except Exception as e:
        logger.warning(f"JWT token verification failed: {str(e)}")
        return None


def extract_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Extract user information from a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        User information dictionary if token is valid, None otherwise
    """
    payload = verify_jwt_token(token)
    if payload:
        return {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "metadata": payload.get("user_metadata", {}),
        }
    return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from Supabase by user ID.
    
    Note: This requires a service role key for admin access.
    For regular operations, use the token-based approach.
    
    Args:
        user_id: Supabase user ID
        
    Returns:
        User information dictionary if found, None otherwise
    """
    try:
        supabase = get_supabase_client()
        # This requires service role key (admin access)
        # Check if we have service role key
        if not settings.supabase_key or "service_role" not in str(settings.supabase_key):
            logger.warning("Service role key required for get_user_by_id")
            return None
        
        # Note: Admin methods may vary by Supabase client version
        # This is a placeholder - adjust based on your Supabase client version
        try:
            # Try admin method if available
            if hasattr(supabase.auth, "admin"):
                response = supabase.auth.admin.get_user_by_id(user_id)
                if response and hasattr(response, "user") and response.user:
                    return {
                        "id": response.user.id,
                        "email": response.user.email,
                        "metadata": response.user.user_metadata or {},
                    }
        except AttributeError:
            logger.warning("Admin methods not available with current Supabase client")
        
        return None
        
    except Exception as e:
        logger.warning(f"Failed to get user by ID: {str(e)}")
        return None

