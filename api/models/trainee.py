from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, Union, List
from datetime import date, datetime
import json
import re

class ConfigInfo(BaseModel):
    run_stage: str
    batch: Optional[str] = ""  # For single trainee creation
    role: str = "trainee"
    is_mock: bool = False
    group_id: Optional[str] = ""
    sheet_id: Optional[str] = None
    sheet_name: Optional[str] = None
    login_url: Optional[str] = None  # Optional login URL for trainee welcome emails

class TraineeInfo(BaseModel):
    name: str
    email: str
    password: Optional[str] = None
    status: Optional[str] = "Accepted"
    nationality: Optional[str] = ""
    gender: Optional[str] = ""
    date_of_birth: Optional[str] = None
    vulnerable: Optional[str] = ""
    city_of_residence: Optional[str] = ""
    bio: Optional[str] = ""
    other_info: Optional[Union[Dict[str, Any], str]] = Field(default_factory=dict)

    @validator('name')
    def validate_name(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Name is required and must be a string')
        
        # Remove extra spaces and check if the name is empty after cleaning
        cleaned_name = v.strip()
        if not cleaned_name:
            raise ValueError('Name cannot be empty')
        
        # Basic name validation - should contain at least one letter
        if not any(c.isalpha() for c in cleaned_name):
            raise ValueError('Name must contain at least one letter')
            
        return cleaned_name

    @validator('email')
    def validate_email(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Email is required and must be a string')
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v.strip().lower()):
            raise ValueError('Invalid email format')
        
        return v.strip().lower()

    @validator('status')
    def validate_status(cls, v):
        if not v or v.strip() == "":
            return "Accepted"
        return v

    @validator('nationality')
    def validate_nationality(cls, v):
        if not v or v.strip() == "":
            return ""
        return v.strip()

    @validator('gender')
    def validate_gender(cls, v):
        if not v or v.strip() == "":
            return ""
        return v.strip()

    @validator('vulnerable')
    def validate_vulnerable(cls, v):
        if not v or v.strip() == "":
            return ""
        return v.strip()

    @validator('city_of_residence')
    def validate_city_of_residence(cls, v):
        if not v or v.strip() == "":
            return ""
        return v.strip()

    @validator('bio')
    def validate_bio(cls, v):
        if not v or v.strip() == "":
            return ""
        return v.strip()

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if not v or (isinstance(v, str) and v.strip() == ""):
            return None
        return v

    @validator('other_info')
    def validate_other_info(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v or {}

class TraineeCreate(BaseModel):
    config: ConfigInfo
    trainee: TraineeInfo

class ErrorDetail(BaseModel):
    error_type: str
    error_message: str
    error_location: str
    error_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "error_location": self.error_location,
            "error_data": self.error_data
        }

class TraineeResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[ErrorDetail] = None
    alluser_id: Optional[str] = None
    profile: Optional[dict] = None
    trainee: Optional[dict] = None
    batch_info: Optional[dict] = None

    def to_dict(self) -> Dict[str, Any]:
        response_dict = {
            "success": self.success,
            "message": self.message
        }
        
        if self.data:
            response_dict["data"] = self.data
            
        if self.error:
            response_dict["error"] = self.error.to_dict()
            
        if self.alluser_id:
            response_dict["alluser_id"] = self.alluser_id
            
        if self.profile:
            response_dict["profile"] = self.profile
            
        if self.trainee:
            response_dict["trainee"] = self.trainee
            
        if self.batch_info:
            response_dict["batch_info"] = self.batch_info
            
        return response_dict

    @classmethod
    def success_response(cls, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        response = cls(
            success=True,
            message=message,
            data=data
        )
        return response.to_dict()

    @classmethod
    def error_response(cls, error_type: str, error_message: str, error_location: str, error_data: Dict[str, Any] = None) -> Dict[str, Any]:
        response = cls(
            success=False,
            message="Error occurred during trainee creation",
            error=ErrorDetail(
                error_type=error_type,
                error_message=error_message,
                error_location=error_location,
                error_data=error_data
            )
        )
        return response.to_dict()

# Separate base config for batch processing
class BatchConfig(BaseModel):
    run_stage: str
    batch: Optional[str] = ""  # Using batch instead of batch_id to match API
    role: str = "trainee"
    is_mock: bool = False
    group_id: Optional[str] = None
    delimiter: str = ","
    encoding: str = "utf-8"
    chunk_size: int = 20
    login_url: str  # Login URL will be set from request origin
    admin_email: Optional[str] = None  # Email address for admin notifications
    callback_url: Optional[str] = None  # URL for webhook callbacks
    webhook_secret: Optional[str] = None  # Secret for webhook signatures
    webhook_headers: Optional[Dict[str, str]] = None  # Additional headers for webhook
    webhook_retry_count: Optional[int] = 3  # Number of times to retry failed webhook calls
    webhook_retry_delay: Optional[int] = 5  # Delay in seconds between retries
    required_columns: list[str] = [
        "name", "email"
    ]

    default_password: Optional[str] = "10$Academy"  # Used when password_option is "default"

class BatchTraineeCreate(BaseModel):
    config: BatchConfig
    is_batch: bool = True
    file_content: bytes

class BatchErrorDetail(BaseModel):
    error_type: str
    error_message: str
    error_location: str
    error_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "error_location": self.error_location,
            "error_data": self.error_data
        }

class BatchProcessingResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[BatchErrorDetail] = None
    batch_info: Optional[dict] = None
    total_processed: Optional[int] = 0
    successful: Optional[int] = 0
    failed: Optional[int] = 0
    failed_trainees: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    successful_trainees: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    error_details: Optional[List[Dict[str, str]]] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        response_dict = {
            "success": self.success,
            "message": self.message,
            "total_processed": self.total_processed,
            "successful": self.successful,
            "failed": self.failed
        }
        
        if self.data:
            response_dict["data"] = self.data
            
        if self.error:
            response_dict["error"] = self.error.to_dict()
            
        if self.batch_info:
            response_dict["batch_info"] = self.batch_info
            
        if self.failed_trainees:
            response_dict["failed_trainees"] = self.failed_trainees
            
        if self.successful_trainees:
            response_dict["successful_trainees"] = self.successful_trainees
            
        if self.error_details:
            response_dict["error_details"] = self.error_details
            
        return response_dict

    @classmethod
    def success_response(cls, message: str, data: Dict[str, Any] = None, batch_info: Dict[str, Any] = None) -> Dict[str, Any]:
        response = cls(
            success=True,
            message=message,
            data=data,
            batch_info=batch_info,
            total_processed=data.get("total_processed", 0) if data else 0,
            successful=data.get("successful", 0) if data else 0,
            failed=data.get("failed", 0) if data else 0,
            failed_trainees=data.get("failed_trainees", []) if data else [],
            successful_trainees=data.get("successful_trainees", []) if data else [],
            error_details=data.get("error_details", []) if data else []
        )
        return response.to_dict()

    @classmethod
    def error_response(cls, error_type: str, error_message: str, error_location: str, error_data: Dict[str, Any] = None, batch_info: Dict[str, Any] = None) -> Dict[str, Any]:
        response = cls(
            success=False,
            message="Error occurred during batch processing",
            error=BatchErrorDetail(
                error_type=error_type,
                error_message=error_message,
                error_location=error_location,
                error_data=error_data
            ),
            batch_info=batch_info,
            failed_trainees=[{
                'error_type': error_type,
                'error_message': error_message,
                'error_location': error_location,
                'trainee_data': error_data
            }] if error_data else []
        )
        return response.to_dict() 