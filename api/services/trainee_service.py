from fastapi import HTTPException
import uuid
from typing import Dict, Tuple, Union, Any
import traceback

from review_scripts.strapi_graphql import StrapiGraphql
from review_scripts.strapi_methods import StrapiMethods
from review_scripts.communication_manager import CommunicationManager
from api.models.trainee import TraineeCreate, TraineeResponse
from api.services.data_processor import DataProcessor

class TraineeService:
    def __init__(self, data: TraineeCreate):
        self.trainee_data = data.trainee
        self.config = data.config
        self.sg = StrapiGraphql(run_stage=self.config.run_stage)
        self.sm = StrapiMethods(run_stage=self.config.run_stage)
        self.cm = CommunicationManager()
        self.data_processor = DataProcessor(self.config)
        print(self.sm.apiroot)
        print(self.sg.apiroot)
        
        # Track created resources for cleanup in case of failure
        self.created_resources = {
            'user_id': None,
            'alluser_id': None,
            'profile_id': None,
            'trainee_id': None
        }

    def _cleanup_resources(self, error_step: str):
        """Clean up created resources if an error occurs"""
        try:
            if error_step == 'alluser' and self.created_resources['user_id']:
                self.cm.delete_user(self.sg, self.created_resources['user_id'])
                
            elif error_step == 'profile':
                if self.created_resources['alluser_id']:
                    self.cm.delete_alluser(self.sg, self.created_resources['alluser_id'])
                if self.created_resources['user_id']:
                    self.cm.delete_user(self.sg, self.created_resources['user_id'])
                    
            elif error_step == 'trainee':
                if self.created_resources['trainee_id']:
                    self.cm.delete_trainee(self.sg, self.created_resources['trainee_id'])
                if self.created_resources['profile_id']:
                    self.cm.delete_profile(self.sg, self.created_resources['profile_id'])
                if self.created_resources['alluser_id']:
                    self.cm.delete_alluser(self.sg, self.created_resources['alluser_id'])
                if self.created_resources['user_id']:
                    self.cm.delete_user(self.sg, self.created_resources['user_id'])
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    def _insert_user_and_alluser(self, user_data: Dict) -> Union[Tuple[str, str], Dict[str, Any]]:
        """Insert user into both users and allusers tables"""
        try:
            # Create user
            result_json = self.cm.create_user(self.sg, user_data)
            user_id = result_json['data']['register']['user']['id']
            self.created_resources['user_id'] = user_id
         
            # Create alluser
            alluser_data = {
                "name": user_data["name"],
                "email": user_data["email"],
                "role": user_data["role"],
                "userId": user_id,
                "batchId": user_data["batch_id"],
                "groups": user_data["groups"]
            }
            alluser_result = self.cm.insert_all_users(self.sg, alluser_data)
            alluser_id = alluser_result['data']['createAllUser']['data']['id']
            self.created_resources['alluser_id'] = alluser_id
            return user_id, alluser_id

        except Exception as e:
            self._cleanup_resources('alluser')
            return TraineeResponse.error_response(
                error_type="ALLUSER_CREATION_ERROR",
                error_message=str(e),
                error_location="alluser_creation",
                error_data=alluser_data
            )

    def _insert_profile(self, profile_data: Dict) -> Dict:
        """Insert profile information"""
        try:
            result = self.cm.insert_profile_information(self.sg, profile_data)
            if result and 'id' in result['data']['createProfileInformation']['data']:
                self.created_resources['profile_id'] = result['data']['createProfileInformation']['data']['id']
            return result
        except Exception as e:
            self._cleanup_resources('profile')
            return TraineeResponse.error_response(
                error_type="PROFILE_CREATION_ERROR",
                error_message=str(e),
                error_location="profile_creation",
                error_data=profile_data
            )

    def _insert_trainee(self, trainee_data: Dict) -> Dict:
        """Insert trainee information"""
        try:
            result = self.sm.insert_data(trainee_data, "trainees")
            if result and 'id' in result:
                self.created_resources['trainee_id'] = result['id']
            return result
        except Exception as e:
            self._cleanup_resources('trainee')
            return TraineeResponse.error_response(
                error_type="TRAINEE_CREATION_ERROR",
                error_message=str(e),
                error_location="trainee_creation",
                error_data=trainee_data
            )

    def create_trainee_services(self) -> Dict[str, Any]:
        """Create a new trainee with all related information"""
        try:
            # Process trainee data
            processed_data = self.data_processor.process_single_trainee(self.trainee_data)

            # Split name into first and last name
            name_parts = processed_data['name'].split()
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            # Create user and alluser
            user_data = {
                "name": processed_data['name'],
                "email": processed_data['email'],
                "role": processed_data['role'],
                "batch_id": processed_data['batch_id'],
                "groups": processed_data['groups'],
                "password": processed_data['password']
            }
            
            user_result = self._insert_user_and_alluser(user_data)
            if isinstance(user_result, dict):
                return user_result

            user_id, alluser_id = user_result

            # Create profile
            profile_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": processed_data['email'],
                "nationality": processed_data['nationality'],
                "gender": processed_data['gender'],
                "date_of_birth": processed_data['date_of_birth'],
                "all_user": alluser_id,
                "other_info": {
                    **processed_data.get('other_info', {}),
                    "vulnerable": processed_data.get('vulnerable', '')
                },
                "bio": processed_data.get('bio', ''),
                "city_of_residence": processed_data.get('city_of_residence', '')
            }
            profile_result = self._insert_profile(profile_data)
            if isinstance(profile_result, dict) and 'error' in profile_result:
                return profile_result

            # Create trainee
            trainee_data = {
                "email": processed_data['email'],
                "trainee_id": str(uuid.uuid4()),
                "Status": processed_data.get('status', 'Accepted'),
                "batch": processed_data['batch_id'],
                "all_user": alluser_id
            }
            trainee_result = self._insert_trainee(trainee_data)
            if isinstance(trainee_result, dict) and 'error' in trainee_result:
                return trainee_result

            return TraineeResponse.success_response(
                message="Trainee created successfully",
                data={
                    "alluser_id": alluser_id,
                "profile": profile_result,
                "trainee": trainee_result
                }
            )
            
        except Exception as e:
            return TraineeResponse.error_response(
                error_type="UNEXPECTED_ERROR",
                error_message=str(e),
                error_location="trainee_creation",
                error_data={"traceback": traceback.format_exc()}
            )
   