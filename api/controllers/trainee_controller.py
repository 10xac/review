from fastapi import HTTPException
from typing import Dict
from fastapi import BackgroundTasks
import logging

from api.models.trainee import TraineeCreate, TraineeResponse, ConfigInfo
from api.services.trainee_service import TraineeService
from api.services.email_service import EmailService

logger = logging.getLogger(__name__)

class TraineeController:
    def __init__(self):
        self.email_service = EmailService()

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

    async def create_admin_trainee_controller(self, trainee: TraineeCreate, background_tasks: BackgroundTasks) -> TraineeResponse:
        """
        Controller method to handle admin trainee creation with mock/real user options
        """
        try:
            service = TraineeService(trainee)
            result = service.create_trainee_services()
        
            # If successful and not a mock user, send welcome email
            if result.get('success') and not trainee.config.is_mock:
                # Use login URL from config if provided, otherwise use default based on run stage
                
                login_url = trainee.config.login_url or f"https://{trainee.config.run_stage}.10academy.org/login"
                
                # background_tasks.add_task(
                #     self._send_welcome_email,
                #     trainee.trainee.email,
                #     trainee.trainee.name,
                #     trainee.trainee.password,
                #     login_url
                # )
            
            return TraineeResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def _send_welcome_email(self, email: str, username: str, password: str, login_url: str):
        """
        Send welcome email to trainee
        """
        try:
            await self.email_service.send_trainee_welcome_email(
                email=email,
                username=username,
                password=password,
                login_url=login_url
            )
            
            logger.info(
                "Trainee welcome email delivered",
                extra={
                    'notification_type': 'trainee_welcome',
                    'receiver': email,
                    'status': 'delivered'
                }
            )
        except Exception as e:
            logger.error(
                "Failed to send trainee welcome email",
                extra={
                    'notification_type': 'trainee_welcome',
                    'receiver': email,
                    'error': str(e)
                }
            )

    # async def process_batch_trainees(self, config: Dict):
    #     """
    #     Controller method to handle batch trainee processing
    #     """
    #     try:
    #         # Create a dummy TraineeCreate object with just the config
    #         trainee_data = TraineeCreate(
    #             config=ConfigInfo(**config),
    #             trainee=None  # This will be set in the service for each row
    #         )
    #         service = TraineeService(trainee_data)
    #         result = service.process_batch_trainees()
    #         return result
    #     except Exception as e:
    #         raise HTTPException(status_code=400, detail=str(e)) 