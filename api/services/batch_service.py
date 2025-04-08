from fastapi import HTTPException
import uuid
import pandas as pd
from typing import Dict, Tuple, List, Union, Any
import time
import io
import traceback
from datetime import datetime
import logging

from review_scripts.strapi_graphql import StrapiGraphql
from review_scripts.strapi_methods import StrapiMethods
from review_scripts.communication_manager import CommunicationManager
from api.models.trainee import BatchTraineeCreate, TraineeCreate, ConfigInfo, TraineeInfo
from api.services.trainee_service import TraineeService
from api.services.data_processor import DataProcessor
from api.services.webhook_service import WebhookService
from api.models.trainee import BatchProcessingResponse

logger = logging.getLogger(__name__)

class BatchService:
    def __init__(self, data: BatchTraineeCreate):
        self.batch_data = data
        self.config = data.config
        self.sg = StrapiGraphql(run_stage=self.config.run_stage)
        self.sm = StrapiMethods(run_stage=self.config.run_stage)
        self.cm = CommunicationManager()
        self.data_processor = DataProcessor(self.config)
        
        # Initialize webhook service if callback_url is provided
        self.webhook_service = None
        if self.config.callback_url:
            try:
                self.webhook_service = WebhookService(self.config)
                logger.info(f"Webhook service initialized for batch {self.config.batch}")
            except Exception as e:
                logger.error(f"Failed to initialize webhook service: {str(e)}")
                # Continue without webhook service
        
        # Track created resources for cleanup in case of failure
        self.created_resources = {
            'user_id': None,
            'alluser_id': None,
            'profile_id': None,
            'trainee_id': None
        }

    def _cleanup_resources(self, error_step: str):
        """
        Clean up created resources if an error occurs
        Args:
            error_step: The step where the error occurred
        """
        try:
            if error_step == 'alluser' and self.created_resources['user_id']:
                # Delete the user if alluser creation failed
                print(f"Cleaning up user {self.created_resources['user_id']}")
                self.cm.delete_user(self.sg, self.created_resources['user_id'])
                
            elif error_step == 'profile':
                # Delete alluser and user if profile creation failed
                if self.created_resources['alluser_id']:
                    print(f"Cleaning up alluser {self.created_resources['alluser_id']}")
                    self.cm.delete_alluser(self.sg, self.created_resources['alluser_id'])
                if self.created_resources['user_id']:
                    print(f"Cleaning up user {self.created_resources['user_id']}")
                    self.cm.delete_user(self.sg, self.created_resources['user_id'])
                    
            elif error_step == 'trainee':
                # Delete trainee, profile, alluser, and user if trainee creation failed
                if self.created_resources['trainee_id']:
                    print(f"Cleaning up trainee {self.created_resources['trainee_id']}")
                    self.cm.delete_trainee(self.sg, self.created_resources['trainee_id'])
                if self.created_resources['profile_id']:
                    print(f"Cleaning up profile {self.created_resources['profile_id']}")
                    self.cm.delete_profile(self.sg, self.created_resources['profile_id'])
                if self.created_resources['alluser_id']:
                    print(f"Cleaning up alluser {self.created_resources['alluser_id']}")
                    self.cm.delete_alluser(self.sg, self.created_resources['alluser_id'])
                if self.created_resources['user_id']:
                    print(f"Cleaning up user {self.created_resources['user_id']}")
                    self.cm.delete_user(self.sg, self.created_resources['user_id'])
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            # Continue with the original error even if cleanup fails

    def _insert_user_and_alluser(self, user_data: Dict) -> Tuple[str, str]:
        """
        Insert user into both users and allusers tables
        Returns tuple of (user_id, alluser_id)
        """
        # 1. First create the user
        try:
            result_json = self.cm.create_user(self.sg, user_data)
            user_id = result_json['data']['register']['user']['id']
            self.created_resources['user_id'] = user_id
         
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail={
                    "error": "USER_CREATION_ERROR",
                    "description": f"Could not create user: {str(e)}",
                    "data": user_data
                }
            )

        # 2. Then create the alluser entry
        try:
            alluser_data = {
                "name": user_data["name"],
                "email": user_data["email"],
                "role": user_data["role"],
                "batch": user_data["batch"],
                "userId": user_id,
                "batchId": user_data["batch_id"]
           
            }

            alluser_result = self.cm.insert_all_users(self.sg, alluser_data)
            alluser_id = alluser_result['data']['createAllUser']['data']['id']
            self.created_resources['alluser_id'] = alluser_id
            return user_id, alluser_id
        except Exception as e:
            self._cleanup_resources('alluser')
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "ALLUSER_CREATION_ERROR",
                    "description": f"Could not create alluser entry: {str(e)}",
                    "data": alluser_data
                }
            )

    def _insert_profile(self, profile_data: Dict):
        """Insert profile information"""
        try:
            result = self.cm.insert_profile_information(self.sg, profile_data)

            if result and 'id' in result['data']['createProfileInformation']['data']:
                self.created_resources['profile_id'] = result['data']['createProfileInformation']['data']['id']
            return result
        except Exception as e:
            self._cleanup_resources('profile')
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "PROFILE_CREATION_ERROR",
                    "description": f"Could not create profile: {str(e)}",
                    "data": profile_data
                }
            )

    def _insert_trainee(self, trainee_data: Dict):
        """Insert trainee information"""
        try:
            result = self.sm.insert_data(trainee_data, "trainees")
            if result and 'id' in result:
                self.created_resources['trainee_id'] = result['id']
            return result
        except Exception as e:
            self._cleanup_resources('trainee')
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "TRAINEE_CREATION_ERROR",
                    "description": f"Could not create trainee: {str(e)}",
                    "data": trainee_data
                }
            )



    def process_trainee_data(self, row_data: Dict) -> Dict:
        """Process a single row of trainee data"""
        processed_data = {}
        
        # Process required fields
        processed_data['name'] = str(row_data.get('name', '')).strip()
        processed_data['email'] = str(row_data.get('email', '')).strip().lower()
        
        # Process optional fields with NaN handling
        for field in ['nationality', 'gender', 'date_of_birth', 'vulnerable', 'bio', 'city_of_residence']:
            value = row_data.get(field)
            if pd.isna(value):  # Handle NaN values
                processed_data[field] = ''
            else:
                processed_data[field] = str(value).strip()
        
        # Add config information
        processed_data['role'] = self.config.role or 'trainee'
        processed_data['batch_id'] = self.config.batch
        processed_data['groups'] = [self.config.group_id] if self.config.group_id else []
        processed_data['status'] = 'Accepted'
        
        essential_fields = ['name', 'email', 'nationality', 'gender', 'date_of_birth', 
                            'vulnerable', 'bio', 'city_of_residence', 'role', 'batch_id', 'groups', 'status']
        # move columns other than the essential feild to other_info
        other_info = {k: v for k, v in processed_data.items() if k not in essential_fields}
        processed_data['other_info'] = other_info
        
        return processed_data

    async def process_batch_trainees(self) -> Dict:
        """Process batch of trainees from CSV data"""
        try:
            # Read CSV data
            df = pd.read_csv(
                io.BytesIO(self.batch_data.file_content),
                delimiter=self.config.delimiter,
                encoding=self.config.encoding
            )
            
            # Initialize counters
            total = len(df)
            successful = 0
            failed = 0
            errors = []
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Convert row to dict and process
                    row_dict = row.to_dict()
                    processed_data = self.process_trainee_data(row_dict)
                    
                    # Validate required fields
                    if not processed_data['name'] or not processed_data['email']:
                        raise ValueError("Missing required fields: name and email must not be empty")
                    
                    # Create trainee
                    trainee_create = TraineeCreate(
                        config=ConfigInfo(
                            run_stage=self.config.run_stage,
                            batch=str(self.config.batch),
                            role=self.config.role,
                            group_id=self.config.group_id
                        ),
                        trainee=TraineeInfo(**processed_data)
                    )
                    
                    # Process trainee
                    trainee_service = TraineeService(trainee_create)
                    result = await trainee_service.create_trainee_services()
                    
                    if result.get('success', False):
                        successful += 1
                    else:
                        failed += 1
                        errors.append({
                            'row': index + 1,
                            'error': str(result.get('error', {}).get('error_message', 'Unknown error')),
                            'data': processed_data
                        })
                        
                except Exception as e:
                    failed += 1
                    errors.append({
                        'row': index + 1,
                        'error': str(e),
                        'data': row_dict
                    })
            
            # Prepare result
            result = {
                'status': 'completed',
                'total_processed': total,
                'successful': successful,
                'failed': failed,
                'errors': errors,
                'batch': self.config.batch,
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'run_stage': self.config.run_stage,
                    'role': self.config.role,
                    'group_id': self.config.group_id
                }
            }
            
            return result
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'batch': self.config.batch,
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'run_stage': self.config.run_stage,
                    'role': self.config.role,
                    'group_id': self.config.group_id
                }
            } 