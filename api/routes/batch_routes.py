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
    login_url: str = "https://tenxdev.com/login",  # Default login URL
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
        if isinstance(current_user, dict) and "success" in current_user and not current_user["success"]:
            return BatchProcessingResponse.error_response(
                error_type=current_user["error"]["error_type"],
                error_message=current_user["error"]["error_message"],
                error_location=current_user["error"]["error_location"],
                error_data=current_user["error"]["error_data"]
            )
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

        # Validate login_url
        if not re.match(r'^https?://', login_url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="login_url must be a valid HTTP(S) URL"
            )

        # Use authenticated user's email as admin_email
        admin_email = current_user["email"]
        print(f"Using authenticated user's email as admin email: {admin_email}")

        # Validate admin_email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', admin_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid admin email format"
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
                login_url=login_url,
                admin_email=admin_email
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
                # Log the results
                service.logger.info(
                    "Batch processing completed",
                    extra={
                        'batch_id': batch,
                        'total_processed': results.get('total_processed', 0),
                        'successful': results.get('successful', 0),
                        'failed': results.get('failed', 0),
                        'status': results.get('status', 'unknown')
                    }
                )
            except Exception as e:
                service.logger.error(
                    "Batch processing failed",
                    extra={
                        'batch_id': batch,
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    }
                )
        
        # Create service instance
        batch_service = BatchService(batch_create)
        
        # Add the background task
        background_tasks.add_task(process_batch_background, batch_service)
        
        return BatchProcessingResponse.success_response(
            message="Batch processing started",
            data={"status": "processing", "batch": batch},
            batch_info={"batch": batch, "admin_email": admin_email}
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