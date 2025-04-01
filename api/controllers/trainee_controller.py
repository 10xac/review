from fastapi import HTTPException
from typing import Dict

from api.models.trainee import TraineeCreate, TraineeResponse, ConfigInfo
from api.services.trainee_service import TraineeService

class TraineeController:
    async def create_trainee_controller(self, trainee: TraineeCreate) -> TraineeResponse:
        """
        Controller method to handle trainee creation
        """
        try:
            service = TraineeService(trainee)
            result = service.create_trainee_services()
            return TraineeResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def process_batch_trainees(self, config: Dict):
        """
        Controller method to handle batch trainee processing
        """
        try:
            # Create a dummy TraineeCreate object with just the config
            trainee_data = TraineeCreate(
                config=ConfigInfo(**config),
                trainee=None  # This will be set in the service for each row
            )
            service = TraineeService(trainee_data)
            result = service.process_batch_trainees()
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) 