from fastapi import HTTPException
import uuid
import pandas as pd
from typing import Dict, Tuple, List, Union
import time
import io
import traceback

from review_scripts.strapi_graphql import StrapiGraphql
from review_scripts.strapi_methods import StrapiMethods
from review_scripts.communication_manager import CommunicationManager
from api.models.trainee import TraineeCreate, BatchTraineeCreate
from api.services.data_processor import DataProcessor


class TraineeService:
    def __init__(self, data: Union[TraineeCreate, BatchTraineeCreate]):
        if isinstance(data, TraineeCreate):
            self.trainee_data = data.trainee
            self.config = data.config
            self.is_batch = False
        else:
            self.batch_data = data
            self.config = data.config
            self.is_batch = True
            
        self.sg = StrapiGraphql(run_stage=self.config.run_stage)
        self.sm = StrapiMethods(run_stage=self.config.run_stage)
        self.cm = CommunicationManager()
        self.data_processor = DataProcessor(self.config)
        
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
            print("alluser_data ......", alluser_data)
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

    def _insert_group(self):
        """Insert group information"""
        try:
            with_out_group = self.cm.get_all_user_without_group(self.sg)
            with_group = self.cm.get_allUser_by_groupId(self.sg, self.config.group_id)
            group_users = with_out_group + with_group
            group_data = {"groupID":self.config.group_id,"allusersID":group_users }
            result = self.cm.insert_group_information(self.sg, group_data)
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not create group: {str(e)}")

    def _insert_profile(self, profile_data: Dict):
        """Insert profile information"""
        try:
            result = self.cm.insert_profile_information(self.sg, profile_data)
            print("result ......", result)
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

    def _get_batch(self, batch_id: int) -> int:
        """Get Strapi batch ID from batch number"""
        batch_json = self.cm.read_batch_from_batch_ID(self.sg, batch_id= batch_id)
        try:
            batch_df = pd.json_normalize(batch_json['data']['batches']['data'])
            batch = batch_df['attributes.Batch']
          
            return int(batch)
        except:
            raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")

    def create_trainee_services(self) -> Dict:
        """
        Create a new trainee with all related information
        """
        try:
            # Process trainee data
            processed_data = self.data_processor.process_single_trainee(self.trainee_data)
            processed_data['batch'] = self._get_batch(processed_data['batch_id'])

            # Split name into first and last name
            name_parts = processed_data['name'].split()
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            # 1. Create user and alluser
            user_data = {
                "name": processed_data['name'],
                "email": processed_data['email'],
                "role": processed_data['role'],
                "batch": processed_data['batch'],
                "batch_id": processed_data['batch_id']
            }
            user_id, alluser_id = self._insert_user_and_alluser(user_data)

            # 2. Create profile
            profile_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": processed_data['email'],
                "nationality": processed_data['nationality'],
                "gender": processed_data['gender'],
                "date_of_birth": processed_data['date_of_birth'].strftime('%Y-%m-%d') if hasattr(processed_data['date_of_birth'], 'strftime') else processed_data['date_of_birth'],
                "all_user": alluser_id,
                "other_info": {"vulnerable": processed_data.get('vulnerable', '')} if 'vulnerable' in processed_data else {},
                "bio": processed_data.get('bio', ''),
                "city_of_residence": processed_data.get('city_of_residence', '')
            }
            profile_result = self._insert_profile(profile_data)

            # 3. Create trainee
            # batch_id = self._get_batch_id(processed_data['batch'])
            trainee_data = {
                "email": processed_data['email'],
                "trainee_id": str(uuid.uuid4()),
                "Status": processed_data.get('status', 'Accepted'),
                "batch": processed_data['batch_id'],
                "all_user": alluser_id
            }
       
            trainee_result = self._insert_trainee(trainee_data)

            return {
                "message": "Trainee created successfully",
                "user_id": alluser_id,
                "profile": profile_result,
                "trainee": trainee_result
            }
        except Exception as e:
            # If any unhandled exception occurs, attempt to clean up all resources
            self._cleanup_resources('trainee')
            raise HTTPException(status_code=400, detail=f"Failed to create trainee: {str(e)}")

    def validate_trainee_data(self, df: pd.DataFrame) -> List[str]:
        """
        Validate the uploaded trainee data
        Args:
            df: DataFrame containing trainee data
        Returns:
            List of error messages, empty if validation passes
        """
        errors = []
        required_columns = ['name', 'email', 'nationality', 'gender', 'date_of_birth']
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check for empty values in required fields
        if not missing_columns:  # Only check if all required columns exist
            for col in required_columns:
                empty_rows = df[df[col].isna() | (df[col] == '')].index.tolist()
                if empty_rows:
                    errors.append(f"Empty values in {col} at rows: {empty_rows}")
        
        # Validate email format
        if 'email' in df.columns:
            invalid_emails = df[~df['email'].str.contains('@', na=False)].index.tolist()
            if invalid_emails:
                errors.append(f"Invalid email format at rows: {invalid_emails}")
        
        # Validate date format
        if 'date_of_birth' in df.columns:
            try:
                pd.to_datetime(df['date_of_birth'])
            except Exception as e:
                errors.append(f"Invalid date format in date_of_birth column: {str(e)}")
        # Fill missing values with empty strings
        
        
        return errors

    async def process_batch_trainees(self) -> Dict:
        """
        Process multiple trainees from uploaded CSV data
        Returns:
            Dict containing results and any errors
        """
        try:
            # Initialize results dictionary with all required keys
            results = {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "created_trainees": [],
                "errors": [],
                "status": "success"
            }

            # Validate batch first
            try:
                batch = self._get_batch(self.config.batch)
                results["batch"] = batch
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "BATCH_VALIDATION_ERROR",
                        "description": f"Failed to validate batch: {str(e)}"
                    }
                )

            # Read CSV data
            try:
                df = pd.read_csv(
                    io.BytesIO(self.batch_data.file_content),
                    delimiter=self.config.delimiter,
                    encoding=self.config.encoding
                )
                df = df.fillna('')
                print(f"Successfully read CSV file with {len(df)} rows")
                results["total"] = len(df)
            except pd.errors.EmptyDataError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "EMPTY_FILE_ERROR",
                        "description": "The uploaded file is empty"
                    }
                )
            except pd.errors.ParserError as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "CSV_PARSE_ERROR",
                        "description": f"Invalid CSV format: {str(e)}"
                    }
                )
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "FILE_READ_ERROR",
                        "description": f"Error reading CSV file: {str(e)}"
                    }
                )
            
            if df.empty:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "EMPTY_DATA_ERROR",
                        "description": "The CSV file contains no data"
                    }
                )
            
            # Print column names for debugging
            print(f"CSV columns: {df.columns.tolist()}")
            
            # Validate required columns
            missing_columns = [col for col in self.config.required_columns if col not in df.columns]
            if missing_columns:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "MISSING_COLUMNS_ERROR",
                        "description": f"Missing required columns: {', '.join(missing_columns)}. Available columns: {', '.join(df.columns)}"
                    }
                )

            # Process in configurable batch sizes
            chunk_size = self.config.chunk_size
            for i in range(0, len(df), chunk_size):
                batch_df = df.iloc[i:i+chunk_size]
                print(f"Processing batch {i//chunk_size + 1} of {(len(df) + chunk_size - 1)//chunk_size}")
                
                for idx, row in batch_df.iterrows():
                    try:
                        print(f"Processing trainee {idx + 1}: {row.get('email', 'Unknown email')}")
                        
                        # Convert row to object-like structure to match single trainee format
                        trainee_data = type('TraineeData', (), {
                            'name': row['name'],
                            'email': row['email'],
                            'nationality': row['nationality'],
                            'gender': row['gender'],
                            'date_of_birth': row['date_of_birth'],
                            'vulnerable': row.get('vulnerable', ''),
                            'bio': row.get('bio', ''),
                            'city_of_residence': row.get('city_of_residence', ''),
                            'status': row.get('status', 'Accepted')
                        })
                        
                        try:
                            # Process and create trainee using the same flow as single trainee
                            processed_data = self.data_processor.process_single_trainee(trainee_data)
                        except Exception as e:
                            raise Exception(f"Data processing failed: {str(e)}")

                        processed_data['batch'] = batch
                        processed_data['batch_id'] = self.config.batch

                        # Create user and alluser
                        user_data = {
                            "name": processed_data['name'],
                            "email": processed_data['email'],
                            "role": processed_data['role'],
                            "batch": processed_data['batch'],
                            "batch_id": processed_data['batch_id']
                        }
                        
                        try:
                            user_id, alluser_id = self._insert_user_and_alluser(user_data)
                        except Exception as e:
                            raise Exception(f"User creation failed: {str(e)}")

                        # Create profile
                        name_parts = processed_data['name'].split()
                        profile_data = {
                            "first_name": name_parts[0],
                            "last_name": " ".join(name_parts[1:]) if len(name_parts) > 1 else "",
                            "email": processed_data['email'],
                            "nationality": processed_data['nationality'],
                            "gender": processed_data['gender'],
                            "date_of_birth": processed_data['date_of_birth'].strftime('%Y-%m-%d') if hasattr(processed_data['date_of_birth'], 'strftime') else processed_data['date_of_birth'],
                            "all_user": alluser_id,
                            "other_info": {"vulnerable": processed_data.get('vulnerable', '')} if 'vulnerable' in processed_data else {},
                            "bio": processed_data.get('bio', ''),
                            "city_of_residence": processed_data.get('city_of_residence', '')
                        }
                        
                        try:
                            profile_result = self._insert_profile(profile_data)
                        except Exception as e:
                            raise Exception(f"Profile creation failed: {str(e)}")

                        # Create trainee
                        trainee_data = {
                            "email": processed_data['email'],
                            "trainee_id": str(uuid.uuid4()),
                            "Status": processed_data.get('status', 'Accepted'),
                            "batch": processed_data['batch_id'],
                            "all_user": alluser_id
                        }
                        
                        try:
                            trainee_result = self._insert_trainee(trainee_data)
                        except Exception as e:
                            raise Exception(f"Trainee creation failed: {str(e)}")

                        results["successful"] += 1
                        results["created_trainees"].append({
                            "email": processed_data['email'],
                            "user_id": alluser_id
                        })

                    except Exception as e:
                        error_msg = {
                            "row": idx + 1,
                            "email": row.get('email', 'Unknown'),
                            "error": str(e),
                            "step": "trainee_creation",
                            "details": traceback.format_exc()
                        }
                        print(f"Error processing trainee: {error_msg}")
                        results["failed"] += 1
                        results["errors"].append(error_msg)
                        self._cleanup_resources('trainee')

                # Add a small delay between batches to prevent rate limiting
                if i + chunk_size < len(df):
                    time.sleep(1)

            if results["failed"] > 0:
                results["status"] = "partial_success"
                print(f"Warning: {results['failed']} trainees failed to process")
                print("Errors:", results["errors"])

            return results
            
        except HTTPException as http_error:
            # Re-raise HTTP exceptions with their original details
            raise http_error
        except Exception as e:
            error_detail = {
                "error": "BATCH_PROCESSING_ERROR",
                "description": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"Error in batch processing: {error_detail}")
            raise HTTPException(
                status_code=400,
                detail=error_detail
            )
   