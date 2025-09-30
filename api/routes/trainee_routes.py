from fastapi import APIRouter, Depends, UploadFile, File
from typing import Optional, Dict
from fastapi import BackgroundTasks

from api.controllers.trainee_controller import TraineeController
from api.models.trainee import (
    TraineeCreate, 
    TraineeResponse, 
    BatchTraineeCreate,
    BatchConfig,
    BatchProcessingResponse
)
from api.core.auth import get_current_user, verify_admin_access

router = APIRouter(prefix="/trainee", tags=["trainee"])

@router.post("/single", response_model=TraineeResponse)
async def create_trainee_route(
    trainee: TraineeCreate,
    controller: TraineeController = Depends(),
    # current_user: Dict = Depends(get_current_user)
):
    """
    Create a new trainee with all related information
    
    The request should include both trainee information and configuration details.
    Example:
    {
        "config": {
            "run_stage": "prod",
            "batch": 5,
            "role": "trainee",
            "group_id": "12"
        },
        "trainee": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "password",
            "nationality": "Kenya",
            "gender": "Male",
            "date_of_birth": "1995-01-01",
            "vulnerable": "No"
        }
    }
    """
 
    
    return await controller.create_trainee_controller(trainee)

@router.post("/admin-single", response_model=TraineeResponse)
async def create_admin_trainee_route(
    trainee: TraineeCreate,
    background_tasks: BackgroundTasks,
    controller: TraineeController = Depends(),
    current_user: Dict = Depends(verify_admin_access)
):
    """
    Create a new trainee as an admin with additional features:
    1. Create mock user (when is_mock=True in config)
    2. Create real user and send welcome email (when is_mock=False in config)
    
    The request should include both trainee information and configuration details.
    Example:
    {
        "config": {
            "run_stage": "prod",
            "batch": 5,
            "role": "trainee",
            "group_id": "12",
            "is_mock": false
        },
        "trainee": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "password",
            "nationality": "Kenya",
            "gender": "Male",
            "date_of_birth": "1995-01-01",
            "vulnerable": "No"
        }
    }
    """
    # Check if current_user is an error response
    if isinstance(current_user, dict) and "success" in current_user and not current_user["success"]:
        return TraineeResponse.error_response(
            error_type=current_user["error"]["error_type"],
            error_message=current_user["error"]["error_message"],
            error_location=current_user["error"]["error_location"],
            error_data=current_user["error"]["error_data"]
        )

    return await controller.create_admin_trainee_controller(trainee, background_tasks)

