from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import date, datetime

class ConfigInfo(BaseModel):
    run_stage: str
    batch: int  # For single trainee creation
    role: str = "trainee"
    group_id: Optional[str] = None
    sheet_id: Optional[str] = None
    sheet_name: Optional[str] = None

class TraineeInfo(BaseModel):
    name: str
    email: EmailStr
    nationality: str
    gender: str
    date_of_birth: Optional[date] = None
    vulnerable: Optional[str] = ""
    status: str = "Accepted"
    city_of_residence: Optional[str] = ""
    bio: Optional[str] = ""

class TraineeCreate(BaseModel):
    config: ConfigInfo
    trainee: TraineeInfo

class TraineeResponse(BaseModel):
    message: str
    user_id: int
    profile: dict
    trainee: dict
    batch_info: Optional[dict] = None

# Separate base config for batch processing
class BatchConfig(BaseModel):
    run_stage: str
    batch: int  # Using batch instead of batch_id to match API
    role: str = "trainee"
    group_id: Optional[str] = None
    delimiter: str = ","
    encoding: str = "utf-8"
    chunk_size: int = 20
    required_columns: list[str] = [
        "name", "email", "nationality", "gender", "date_of_birth"
    ]

class BatchTraineeCreate(BaseModel):
    config: BatchConfig
    is_batch: bool = True
    file_content: bytes

class BatchProcessingResponse(BaseModel):
    message: str
    details: dict
    batch_info: dict 