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
from api.core.auth import get_current_user

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
    # print("Trainee data:", trainee)
    # print("Current user:", current_user)
    # # Verify admin access after getting the trainee data
    # if current_user.get("role") not in ["Authenticated", "Staff"]:
    #     return TraineeResponse.error_response(
    #         error_type="AUTH_ERROR",
    #         error_message="Insufficient permissions. Admin access required.",
    #         error_location="trainee_creation",
    #         error_data={"user_role": current_user.get("role")}
    #     )
    
    return await controller.create_trainee_controller(trainee)

