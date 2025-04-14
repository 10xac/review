import httpx
import asyncio
from datetime import datetime
import hmac
import hashlib
import json
from typing import Dict, Optional, List
import logging
import pandas as pd
import math

logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self, config):
        if not config.callback_url:
            raise ValueError("callback_url is required for webhook service")
            
        self.config = config
        self.callback_url = config.callback_url
        self.webhook_secret = config.webhook_secret or "local-development-secret-key"
        self.webhook_headers = config.webhook_headers or {}
        self.retry_count = max(1, min(config.webhook_retry_count or 1, 10))
        self.retry_delay = max(1, min(config.webhook_retry_delay or 1, 60))
        
        logger.info(f"Webhook service initialized for {self.callback_url}")

    def _generate_webhook_signature(self, payload: Dict) -> str:
        """
        Generate HMAC signature for webhook payload
        Args:
            payload: The data to be sent in the webhook
        Returns:
            str: The generated signature
        """
        try:
            if not self.webhook_secret:
                return ""
                
            payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
            signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            return signature
        except Exception as e:
            logger.error(f"Error generating webhook signature: {str(e)}")
            return ""

    def _sanitize_payload(self, payload: Dict) -> Dict:
        """Sanitize the payload to ensure it's JSON serializable"""
        def sanitize_value(value):
            # Handle pandas Series
            if isinstance(value, pd.Series):
                return sanitize_value(value.to_dict())
                
            # Handle pandas DataFrame
            if isinstance(value, pd.DataFrame):
                return sanitize_value(value.to_dict())
                
            # Handle dictionaries
            if isinstance(value, dict):
                return {k: sanitize_value(v) for k, v in value.items()}
                
            # Handle lists/tuples
            if isinstance(value, (list, tuple)):
                return [sanitize_value(v) for v in value]
                
            # Handle NaN/None values
            try:
                if value is None or (isinstance(value, float) and math.isnan(value)):
                    return None
            except (TypeError, ValueError):
                pass
                
            # Handle basic types
            if isinstance(value, (int, float, str, bool)):
                return value
                
            # Convert anything else to string
            return str(value)
        
        try:
            # First pass: sanitize the values
            sanitized = sanitize_value(payload)
            
            # Second pass: verify JSON serialization
            json.dumps(sanitized)
            return sanitized
            
        except Exception as e:
            logger.error(f"Error sanitizing payload: {str(e)}")
            # Return a simplified error response
            return {
                'event': 'batch.processed',
                'status': 'error',
                'error': f'Failed to serialize payload: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

    async def _send_webhook_with_retry(self, payload: Dict, headers: Dict) -> bool:
        """
        Send webhook with retry mechanism
        Args:
            payload: The data to be sent in the webhook
            headers: The headers to be sent with the webhook
        Returns:
            bool: True if webhook was successfully sent, False otherwise
        """
        if not self.callback_url:
            logger.warning("No callback URL provided, skipping webhook")
            return False

        retry_count = self.retry_count
        retry_delay = self.retry_delay

        for attempt in range(retry_count):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        self.callback_url,
                        json=payload,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201, 202]:
                        logger.info(f"Webhook delivered successfully on attempt {attempt + 1}")
                        return True
                    else:
                        logger.warning(
                            f"Webhook delivery failed with status {response.status_code} "
                            f"on attempt {attempt + 1}. Response: {response.text}"
                        )
                        
            except httpx.TimeoutException:
                logger.warning(f"Webhook delivery attempt {attempt + 1} timed out")
            except Exception as e:
                logger.error(f"Webhook delivery attempt {attempt + 1} failed: {str(e)}")

            if attempt < retry_count - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        logger.error(f"Webhook delivery failed after {retry_count} attempts")
        return False

    async def notify_callback(self, results: Dict) -> None:
        """Send webhook notification with processing results"""
        try:
            # Prepare webhook payload
            payload = {
                'event': 'batch.processed',
                'status': results.get('status', 'unknown'),
                'total_processed': results.get('total_processed', 0),
                'successful': results.get('successful', 0),
                'failed': results.get('failed', 0),
                'errors': results.get('errors', []),
                'batch': results.get('batch'),
                'timestamp': datetime.now().isoformat(),
                'metadata': results.get('metadata', {})
            }
            
            # Sanitize the payload
            sanitized_payload = self._sanitize_payload(payload)
            
            # Generate signature
            signature = self._generate_webhook_signature(sanitized_payload)
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'X-Webhook-Signature': signature
            }
            if self.webhook_headers:
                headers.update(self.webhook_headers)
            
            # Send webhook with retry
            await self._send_webhook_with_retry(sanitized_payload, headers)
            
        except Exception as e:
            print(f"Failed to deliver webhook: {str(e)}") 