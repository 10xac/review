from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from typing import Optional
from functools import lru_cache

from utils.secret import get_auth

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

@lru_cache()
def get_api_key(run_stage: str) -> str:
    """Get API key from secrets manager"""
    try:
        return get_auth(f'strapi_{run_stage}', envvar='STRAPI_TOKEN')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not get API key: {str(e)}"
        )

async def verify_api_key(
    api_key: str = Security(api_key_header),
    run_stage: Optional[str] = "prod"
) -> bool:
    """Verify API key from request header"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )
    
    try:
        valid_key = get_api_key(run_stage)
        if api_key == valid_key:
            return True
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying API key: {str(e)}"
        ) 