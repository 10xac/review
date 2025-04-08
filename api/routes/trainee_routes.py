from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import Optional, Dict
from fastapi import BackgroundTasks
import httpx
import json
import pandas as pd
import io
import traceback
import os

from fastapi import FastAPI, Request, Header
import hmac
import hashlib
import json

app = FastAPI()

from api.controllers.trainee_controller import TraineeController
from api.models.trainee import (
    TraineeCreate, 
    TraineeResponse, 
    BatchTraineeCreate,
    BatchConfig,
    BatchProcessingResponse
)
from api.services.trainee_service import TraineeService



router = APIRouter(prefix="/trainee", tags=["trainee"])

@router.post("/single", response_model=TraineeResponse)
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
            "password": "password",
            "nationality": "Kenya",
            "gender": "Male",
            "date_of_birth": "1995-01-01",
            "vulnerable": "No"
        }
    }
    """
    return await controller.create_trainee_controller(trainee)

