#!/usr/bin/env python3
"""SLM API client for code generation with retry logic"""

import requests
import logging
from typing import Optional, Dict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class SLMAPIClient:
    """Interface to Small Language Model API with retry logic"""
    
    def __init__(self, api_url: str, model: str, max_length: int, timeout: int):
        """
        Initialize SLM API client with automatic retry capability
        
        Args:
            api_url: Base URL of SLM API
            model: Model name/identifier
            max_length: Maximum generation length
            timeout: Request timeout in seconds
        """
        self.api_url = api_url
        self.model = model
        self.max_length = max_length
        self.timeout = timeout
        
        # Create session with retry logic
        self.session = self._create_retry_session()
        
        logger.info(f"Initialized SLM API Client with retry logic")
        logger.info(f"  URL: {api_url}")
        logger.info(f"  Model: {model}")
        logger.info(f"  Max length: {max_length}")
        logger.info(f"  Retry: 10 attempts with backoff_factor=1.5")
    
    def _create_retry_session(self) -> requests.Session:
        """
        Create requests session with retry strategy
        
        Retry Configuration:
        - Total attempts: 10
        - Backoff factor: 1.5 (wait times: 1.5s, 3s, 6s, 12s, 24s, 48s, 96s, 192s, 384s)
        - Retry on: Server errors (500, 502, 503, 504), Timeouts (408, 429)
        
        Returns:
            Configured requests.Session with retry logic
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=10,                          # Maximum 10 retry attempts
            backoff_factor=1.5,                # Exponential backoff: 1.5s, 3s, 6s, 12s...
            status_forcelist=[500, 502, 503, 504, 408, 429],  # HTTP codes to retry
            allowed_methods=["POST"],          # Allow retries for POST requests
            raise_on_status=False              # Don't raise exceptions, return response
        )
        
        # Apply retry strategy to session
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def generate(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """
        Generate code using SLM API with automatic retry logic
        
        If the API is unresponsive or returns errors, this method will automatically:
        - Retry up to 10 times
        - Use exponential backoff (1.5s, 3s, 6s, 12s, 24s, 48s, 96s, 192s, 384s)
        - Retry on server errors (500, 502, 503, 504) and timeouts (408, 429)
        
        Args:
            prompt: Input prompt with TASK, REQUIREMENTS, etc.
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            Generated text or None on failure after all retries exhausted
        """
        try:
            payload = {
                "prompt": prompt,
                "max_length": self.max_length,
                "model": self.model,
                "temperature": temperature
            }
            
            logger.info(f"Calling SLM API with retry logic: {self.api_url}/generate")
            logger.info(f"  Model: {self.model}, Temperature: {temperature}")
            logger.info(f"  Prompt length: {len(prompt)} chars")
            logger.info(f"  Will retry up to 10 times with exponential backoff if needed")
            
            # Use session with retry logic instead of direct requests.post()
            response = self.session.post(
                f"{self.api_url}/generate",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Try multiple field names that different SLM APIs might use
                for field in ['generated_text', 'text', 'response', 'output', 'result']:
                    if field in data:
                        result = data[field]
                        logger.info(f"Received {len(result)} bytes from SLM (field: {field})")
                        return result
                
                # Fallback: return whole response as string
                result = str(data)
                logger.warning(f"Unknown response format, returning as string: {len(result)} bytes")
                return result
            else:
                logger.error(f"SLM API error {response.status_code}: {response.text}")
                return None
                
        except requests.Timeout:
            logger.error(f"SLM API timeout after {self.timeout}s")
            return None
        except requests.RequestException as e:
            logger.error(f"SLM API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling SLM API: {e}")
            return None