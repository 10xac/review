from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import Optional, Dict
import pandas as pd
import io
import traceback

from api.controllers.trainee_controller import TraineeController
from api.models.trainee import ( TraineeCreate,
    TraineeResponse, 
    BatchTraineeCreate,
    BatchConfig,
    BatchProcessingResponse
)
from api.services.trainee_service import TraineeService


router = APIRouter(prefix="/trainee", tags=["trainee"])

@router.post("/", response_model=TraineeResponse)
async def create_trainee_route(
    trainee: TraineeCreate,
    controller: TraineeController = Depends()
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
            "nationality": "Kenya",
            "gender": "Male",
            "date_of_birth": "1995-01-01",
            "vulnerable": "No"
        }
    }
    """
    return await controller.create_trainee_controller(trainee)

@router.post("/batch", response_model=BatchProcessingResponse)
async def create_batch_trainees(
    file: UploadFile = File(...),
    run_stage: str = "prod",
    batch: int = None,
    role: str = "trainee",
    group_id: Optional[str] = None,
    delimiter: str = ",",
    encoding: str = "utf-8",
    chunk_size: int = 20
):
    """
    Upload and process multiple trainees from a CSV file
    
    The CSV file should contain the following required columns:
    - name
    - email
    - nationality
    - gender
    - date_of_birth
    
    Optional columns:
    - vulnerable
    - bio
    - city_of_residence
    - status
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
            
        # Validate batch
        if batch is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="batch parameter is required"
            )

        # Validate run_stage
        if not run_stage:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="run_stage parameter is required"
            )
        print(f"run_stage: {run_stage}")
        try:
            # Create config
            config = BatchConfig(
                run_stage=run_stage,
                batch=batch,
                role=role,
                group_id=group_id,
                delimiter=delimiter,
                encoding=encoding,
                chunk_size=chunk_size 
                
            )
        except Exception as config_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid configuration: {str(config_error)}"
            )
        
        try:
            # Read file content
            file_content = await file.read()
            if not file_content:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Empty file provided"
                )
        except Exception as file_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading file: {str(file_error)}"
            )
        
        try:
            # Create BatchTraineeCreate instance
            batch_create = BatchTraineeCreate(
                config=config,
                file_content=file_content
            )
        except Exception as batch_create_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating batch request: {str(batch_create_error)}"
            )
        
        try:
            # Create service instance and process batch
            trainee_service = TraineeService(batch_create)
            results = await trainee_service.process_batch_trainees()
            
            return BatchProcessingResponse(
                message=f"Processed {results['total']} trainees",
                details=results,
                batch_info=results.get('batch_info', {})
            )
        except Exception as processing_error:
            # Log the full error for debugging
            print(f"Error processing batch: {str(processing_error)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing batch: {str(processing_error)}"
            )
        
    except HTTPException as http_error:
        # Re-raise HTTP exceptions as is
        raise http_error
    except Exception as e:
        # Log the unexpected error
        print(f"Unexpected error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 