from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, Union, List
from datetime import date, datetime
import json
import re

class ConfigInfo(BaseModel):
    run_stage: str
    batch: Optional[str] = ""  # For single trainee creation
    role: str = "trainee"
    group_id: Optional[str] = ""
    sheet_id: Optional[str] = None
    sheet_name: Optional[str] = None

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
    batch: Optional[int] = None   # Using batch instead of batch_id to match API
    role: str = "trainee"
    group_id: Optional[str] = None
    delimiter: str = ","
    encoding: str = "utf-8"
    chunk_size: int = 20
    callback_url: Optional[str] = None
    webhook_secret: Optional[str] = None  # Secret key for webhook authentication
    webhook_headers: Optional[Dict[str, str]] = None  # Custom headers for webhook
    webhook_retry_count: int = 3  # Number of retry attempts for failed webhooks
    webhook_retry_delay: int = 5  # Delay between retries in seconds
    required_columns: list[str] = [
        "name", "email"#,  "nationality", "gender", "date_of_birth"
    ]

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
    errors: Optional[List[Dict[str, Any]]] = None

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
            
        if self.errors:
            response_dict["errors"] = self.errors
            
        return response_dict

    @classmethod
    def success_response(cls, message: str, data: Dict[str, Any] = None, batch_info: Dict[str, Any] = None) -> Dict[str, Any]:
        response = cls(
            success=True,
            message=message,
            data=data,
            batch_info=batch_info,
            total_processed=data.get("total", 0) if data else 0,
            successful=data.get("successful", 0) if data else 0,
            failed=data.get("failed", 0) if data else 0,
            errors=data.get("errors", []) if data else []
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
            batch_info=batch_info
        )
        return response.to_dict() 