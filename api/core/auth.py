from typing import Dict, Optional
from fastapi import HTTPException, Security, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx

from review_scripts.communication_manager import CommunicationManager
from review_scripts.strapi_graphql import StrapiGraphql
from api.core.config import Settings
from api.models.trainee import TraineeResponse


security = HTTPBearer()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict:
    """
    Validate the Bearer token and return the current user's information.
    The token is validated against Strapi's /users/me endpoint.
    
    Args:
        request: FastAPI request object to access request body
        credentials: The JWT token credentials
    """
    token = credentials.credentials
    print("token", token)
    
    # Get run_stage from request body
    try:
        form_data = await request.form()
        run_stage = form_data.get("run_stage", "dev")
    except:
        run_stage = "prod"  # Default to prod if can't get from request
    
    sg = StrapiGraphql(run_stage=run_stage)
    strapi_url = sg.apiroot
    print("strapi_url", strapi_url)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    cm = CommunicationManager()
    auth_query = cm.request_auth_query()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(strapi_url, headers=headers, json={"query": auth_query})
            print("Response status:", response.status_code)
            print("Response text:", response.text)
     
            if response.status_code == 200:
                auth_data = response.json()
                print("Authentication response:", auth_data)
                
                if auth_data and "data" in auth_data and "me" in auth_data["data"]:
                    user_data = auth_data["data"]["me"]
                    print("User data:", user_data)

                    # Extract user info
                    uid = user_data.get("id", "")
                    username = user_data.get("username", "")
                    email = user_data.get("email", "")
                    
                    # Extract role
                    role_data = user_data.get("role", {})
                    role = role_data.get("name", "user") if isinstance(role_data, dict) else "user"
                    print(f"Extracted role: {role}")
    
                    return {
                        "id": str(user_data.get("id")),
                        "email": user_data.get("email"),
                        "username": user_data.get("username"),
                        "role": role
                    }
                else:
                    return TraineeResponse.error_response(
                        error_type="AUTH_ERROR",
                        error_message="Invalid authentication data",
                        error_location="token_validation",
                        error_data={"response": auth_data}
                    )
            else:
                return TraineeResponse.error_response(
                    error_type="AUTH_ERROR",
                    error_message="Invalid authentication credentials",
                    error_location="token_validation",
                    error_data={"status_code": response.status_code}
                )
                
    except Exception as e:
        print(f"Exception during authentication: {str(e)}")
        return TraineeResponse.error_response(
            error_type="AUTH_ERROR",
            error_message="Failed to validate authentication token",
            error_location="token_validation",
            error_data={"exception": str(e)}
        )

async def verify_admin_access(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Verify that the current user has admin access
    
    Args:
        current_user: The authenticated user's data
    """
    print("current_user", current_user)
    
    # If current_user is an error response, return it directly
    if isinstance(current_user, dict) and "success" in current_user and not current_user["success"]:
        return current_user
        
    # If current_user doesn't have the required fields, return error
    if not isinstance(current_user, dict) or "role" not in current_user:
        return TraineeResponse.error_response(
            error_type="AUTH_ERROR",
            error_message="Invalid user data received",
            error_location="admin_verification",
            error_data={"user_data": current_user}
        )
        
    if current_user.get("role") not in ["Authenticated", "Staff"]:
        return TraineeResponse.error_response(
            error_type="AUTH_ERROR",
            error_message="Insufficient permissions. Admin access required.",
            error_location="admin_verification",
            error_data={"user_role": current_user.get("role")}
        )
    return current_user 