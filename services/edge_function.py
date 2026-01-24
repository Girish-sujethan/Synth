"""Service for invoking Supabase Edge Functions."""

import requests
from typing import Dict, Any, Optional
from config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class EdgeFunctionService:
    """Service for invoking Supabase Edge Functions."""
    
    def __init__(self):
        """Initialize Edge Function service."""
        if not settings.supabase_url:
            raise ValueError("SUPABASE_URL is not configured")
        
        self.supabase_url = settings.supabase_url
        # Use service role key for Edge Function invocations
        self.service_role_key = settings.supabase_key
    
    def invoke_function(
        self,
        function_name: str,
        payload: Dict[str, Any],
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Invoke a Supabase Edge Function.
        
        Args:
            function_name: Name of the Edge Function
            payload: Request payload to send to the function
            timeout: Request timeout in seconds (default: 300 for long-running functions)
            
        Returns:
            Response data from the Edge Function
            
        Raises:
            ValueError: If configuration is missing
            requests.RequestException: If the request fails
        """
        if not self.service_role_key:
            raise ValueError("SUPABASE_KEY (service role key) is required for Edge Function invocations")
        
        url = f"{self.supabase_url}/functions/v1/{function_name}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.service_role_key}",
        }
        
        try:
            logger.info(f"Invoking Edge Function: {function_name}")
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"Edge Function {function_name} timed out after {timeout}s")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"Edge Function {function_name} returned error: {e.response.status_code}")
            try:
                error_data = e.response.json()
                raise ValueError(f"Edge Function error: {error_data.get('error', e.response.text)}")
            except:
                raise ValueError(f"Edge Function error: {e.response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to invoke Edge Function {function_name}: {str(e)}")
            raise


def get_edge_function_service() -> EdgeFunctionService:
    """Get Edge Function service instance."""
    return EdgeFunctionService()

