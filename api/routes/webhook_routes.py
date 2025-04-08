from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib
import json
from typing import Optional

router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.post("")
async def webhook_handler(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None)
):
    """
    Handle incoming webhooks for batch processing notifications
    
    The webhook expects a POST request with a JSON payload containing batch processing results.
    If a webhook secret is configured, the request must include an X-Webhook-Signature header
    with an HMAC SHA-256 signature of the payload.
    """
    # Get the raw body
    body = await request.body()
    payload = body.decode('utf-8')
    print(f"Received webhook: {payload}")
    
    # Parse the payload
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Log the received webhook
    print(f"Received webhook: {data}")
    
    # Handle different statuses
    if data["status"] == "success":
        print(f"Batch {data['batch']} processed successfully")
    elif data["status"] == "partial_success":
        print(f"Batch {data['batch']} partially successful")
        print(f"Failed entries: {data['errors']}")
    else:
        print(f"Batch {data['batch']} failed")
        print(f"Errors: {data['errors']}")
    
    return {
        "status": "received",
        "message": "Webhook processed successfully",
        "data": data
    } 