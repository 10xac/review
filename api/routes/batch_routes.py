from fastapi import APIRouter, HTTPException, UploadFile, File, status, BackgroundTasks, Depends
from typing import Optional, Dict
import json
import traceback
import re

from api.core.auth import verify_admin_access
from api.models.trainee import BatchConfig, BatchTraineeCreate, BatchProcessingResponse
from api.services.batch_service import BatchService

router = APIRouter(prefix="/trainee", tags=["trainee"])

@router.post("/batch", response_model=BatchProcessingResponse)
async def process_batch( 
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    run_stage: str = "dev",
    batch: int = None,
    role: str = "trainee",
    group_id: Optional[str] = None,
    delimiter: str = ",",
    encoding: str = "utf-8",
    chunk_size: int = 20,
    callback_url: Optional[str] = None,
    webhook_retry_count: Optional[int] = 3,
    webhook_retry_delay: Optional[int] = 5,
    current_user: Dict = Depends(verify_admin_access)
):
    """
    Process a batch of trainees from a CSV file
    
    The CSV file should contain the following required columns:
    - name
    - email
    
    Optional columns:
    - nationality
    - gender
    - date_of_birth
    - vulnerable
    - bio
    - city_of_residence
    - status
    - other_info
    """
    
    try:
        # Validate file
        if not file.filename:
            return BatchProcessingResponse.error_response(
                error_type="VALIDATION_ERROR",
                error_message="No file provided",
                error_location="file_validation",
                error_data={"filename": file.filename}
            )
            
        # Validate batch
        if batch is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="batch parameter is required"
            )

        # Validate callback_url if provided
        if callback_url:
            if not re.match(r'^https?://', callback_url):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="callback_url must be a valid HTTP(S) URL"
                )

        # Validate retry parameters
        if webhook_retry_count is not None and (webhook_retry_count < 1 or webhook_retry_count > 10):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="webhook_retry_count must be between 1 and 10"
            )

        if webhook_retry_delay is not None and (webhook_retry_delay < 1 or webhook_retry_delay > 60):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="webhook_retry_delay must be between 1 and 60 seconds"
            )

        try:
            # Create config
            config = BatchConfig(
                run_stage=run_stage,
                batch=batch,
                role=role,
                group_id=group_id,
                delimiter=delimiter,
                encoding=encoding,
                chunk_size=chunk_size,
                callback_url=callback_url,
                webhook_retry_count=webhook_retry_count,
                webhook_retry_delay=webhook_retry_delay
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
        
        async def process_batch_background(service: BatchService):
            try:
                results = await service.process_batch_trainees()
                if callback_url and service.webhook_service:
                    await service.webhook_service.notify_callback(results)
            except Exception as e:
                print(f"Background task failed: {str(e)}")
                if callback_url and service.webhook_service:
                    error_results = {
                        "status": "failed",
                        "error": str(e),
                        "batch": batch
                    }
                    await service.webhook_service.notify_callback(error_results)
        
        # Create service instance
        batch_service = BatchService(batch_create)
        
        # Add the background task
        background_tasks.add_task(process_batch_background, batch_service)
        
        return BatchProcessingResponse.success_response(
            message="Batch processing started",
            data={"status": "processing", "batch": batch},
            batch_info={"batch": batch, "callback_url": callback_url}
        )
        
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 