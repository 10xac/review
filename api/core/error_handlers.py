from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from api.models.trainee import TraineeResponse

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors
    """
    errors = exc.errors()
    first_error = errors[0]  # Get the first error
    
    # Extract the field name from the error location
    field_name = first_error["loc"][-1] if first_error["loc"] else "unknown"
    
    # Create a standardized error response
    error_response = TraineeResponse.error_response(
        error_type="VALIDATION_ERROR",
        error_message=first_error["msg"],
        error_location=f"{field_name}_validation",
        error_data={"field": field_name, "value": first_error.get("input")}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )

async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """
    Custom handler for Pydantic model validation errors
    """
    errors = exc.errors()
    first_error = errors[0]  # Get the first error
    
    # Extract the field name from the error location
    field_name = first_error["loc"][-1] if first_error["loc"] else "unknown"
    
    # Create a standardized error response
    error_response = TraineeResponse.error_response(
        error_type="VALIDATION_ERROR",
        error_message=first_error["msg"],
        error_location=f"{field_name}_validation",
        error_data={"field": field_name, "value": first_error.get("input")}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    ) 