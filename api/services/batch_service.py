from fastapi import HTTPException
import pandas as pd
from datetime import datetime
import logging
import traceback
from typing import Dict, List, Optional
import io

# Import all your existing classes and models
from review_scripts.strapi_graphql import StrapiGraphql
from review_scripts.strapi_methods import StrapiMethods
from review_scripts.communication_manager import CommunicationManager
from api.models.trainee import BatchTraineeCreate, TraineeCreate, ConfigInfo, TraineeInfo
from api.services.trainee_service import TraineeService
from api.services.data_processor import DataProcessor
from api.services.webhook_service import WebhookService
from api.services.email_service import EmailService
from api.core.logging_config import setup_logging
from api.utils.password_generator import generate_secure_password

logger = logging.getLogger(__name__)

class BatchService:
    def __init__(self, batch_create: BatchTraineeCreate):
        self.batch_create = batch_create
        self.config = batch_create.config
        self.sg = StrapiGraphql(run_stage=self.config.run_stage)
        self.sm = StrapiMethods(run_stage=self.config.run_stage)
        self.cm = CommunicationManager()
        self.data_processor = DataProcessor(self.config)
        self.logger = setup_logging()
        
        # Initialize webhook service if callback_url is provided
        
        self.webhook_service = WebhookService(self.config) if self.config.callback_url else None
        
        # Initialize email service
        self.sender_email = "train@10academy.org"
        self.email_service = None
        if self.config.admin_email:
            try:
                self.email_service = EmailService(source_email=self.sender_email)
                self.logger.info(
                    f"Email service initialized",
                    extra={
                        'sender_email': self.sender_email,
                        'admin_email': self.config.admin_email,
                        'batch_id': self.config.batch
                    }
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to initialize email service",
                    extra={
                        'sender_email': self.sender_email,
                        'admin_email': self.config.admin_email,
                        'error': str(e)
                    }
                )
        
        # Track created resources for cleanup in case of failure
        self.created_resources = {
            'user_id': None,
            'alluser_id': None,
            'profile_id': None,
            'trainee_id': None
        }

    async def process_batch_trainees(self) -> Dict:
        """Main method to process batch of trainees"""
        start_time = datetime.now()
        logger.info(f"Starting batch processing for batch {self.config.batch}")

        try:
            # Process the batch
            results = await self._process_batch_records()
            
            # Send notifications
            await self._send_notifications(results)
            
            # Log completion
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Batch processing completed in {duration:.2f} seconds", extra={
                'results_summary': {
                    'total': results['total_processed'],
                    'successful': results['successful'],
                    'failed': results['failed']
                }
            })
            
            return results
            
        except Exception as e:
            error_response = self._create_error_response(e)
            logger.error("Batch processing failed", extra={
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            
            try:
                await self._send_notifications(error_response)
            except Exception as notify_error:
                logger.error("Failed to send error notifications", extra={
                    'error': str(notify_error)
                })
            
            return error_response

    async def _process_batch_records(self) -> Dict:
        """Process all records in the batch"""
        try:
            # Read and validate CSV
            df = self._read_csv_file()
            if isinstance(df, dict):  # Return early if validation failed
                return df

            total = len(df)
            successful = []
            failed = []
            
            # Process each record
            for index, row in df.iterrows():
                row_num = index + 1
                result = await self._process_trainee_record(row, row_num)
                
                if result['success']:
                    successful.append(result)
                else:
                    failed.append(result)

            return self._compile_results(total, successful, failed)

        except Exception as e:
            logger.error("Error processing batch records", extra={
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            raise

    async def _process_trainee_record(self, row: pd.Series, row_num: int) -> Dict:
        """Process a single trainee record"""
        try:
            row_data = row.to_dict()
            processed_data = self._process_row_data(row_data)
            
            # Validate required fields
            if not processed_data['name'] or not processed_data['email']:
                raise ValueError("Name and email are required fields")
            
            # Create trainee
            trainee_create = TraineeCreate(
                config=ConfigInfo(
                    run_stage=self.config.run_stage,
                    batch=str(self.config.batch),
                    role=self.config.role,
                    group_id=self.config.group_id
                ),
                trainee=TraineeInfo(**{
                    'name': processed_data['name'],
                    'email': processed_data['email'],
                    'password': processed_data['password'],
                    'status': processed_data.get('status', 'Accepted'),
                    'nationality': processed_data.get('nationality', ''),
                    'gender': processed_data.get('gender', ''),
                    'date_of_birth': processed_data.get('date_of_birth'),
                    'vulnerable': processed_data.get('vulnerable', ''),
                    'city_of_residence': processed_data.get('city_of_residence', ''),
                    'bio': processed_data.get('bio', ''),
                    'other_info': processed_data.get('other_info', {})
                })
            )

            # Create trainee via service
            trainee_service = TraineeService(trainee_create)
            result = trainee_service.create_trainee_services()  # Remove await since it's synchronous
            
            if isinstance(result, dict) and result.get('success', False):
                return {
                    'success': True,
                    'row': row_num,
                    'name': processed_data['name'],
                    'email': processed_data['email'],
                    'tenx_id': result.get('data', {}).get('trainee', {}).get('id'),
                    'password': processed_data['password']
                }
            
            # Handle service error
            error_msg = result.get('error', {}).get('error_message', 'Unknown error') if isinstance(result, dict) else str(result)
            logger.error(f"Failed to process trainee at row {row_num}", extra={
                'email': processed_data['email'],
                'error': error_msg,
                'result': str(result)
            })
            return self._create_record_error(row_data, row_num, error_msg)
            
        except Exception as e:
            logger.error(f"Unexpected error processing trainee at row {row_num}", extra={
                'email': row_data.get('email', 'Unknown'),
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            return self._create_record_error(row_data, row_num, str(e))

    def _read_csv_file(self) -> pd.DataFrame:
        """Read and validate CSV file"""
        try:
            df = pd.read_csv(
                io.BytesIO(self.batch_create.file_content),
                delimiter=self.config.delimiter,
                encoding=self.config.encoding
            )
            
            # Validate required columns
            required_columns = {'name', 'email'}
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                return {
                    'status': 'failed',
                    'error': f'Missing required columns: {missing}',
                    'error_type': 'VALIDATION_ERROR',
                    'batch': self.config.batch,
                    'total_processed': 0,
                    'successful': 0,
                    'failed': 0,
                    'failed_trainees': []
                }
            
            # Validate that name and email are not empty
            invalid_rows = df[df['name'].isna() | df['email'].isna() | (df['name'] == '') | (df['email'] == '')]
            if not invalid_rows.empty:
                invalid_row_nums = invalid_rows.index.tolist()
                return {
                    'status': 'failed',
                    'error': f'Invalid data in rows {invalid_row_nums}: name or email is empty',
                    'error_type': 'VALIDATION_ERROR',
                    'batch': self.config.batch,
                    'total_processed': 0,
                    'successful': 0,
                    'failed': 0,
                    'failed_trainees': []
                }
            
            return df
            
        except Exception as e:
            logger.error("Error reading CSV file", extra={
                'error': str(e),
                'traceback': traceback.format_exc(),
                'batch_id': self.config.batch
            })
            raise

    def _process_row_data(self, row_data: Dict) -> Dict:
        """Process and clean row data"""
        processed = {
            'name': str(row_data.get('name', '')).strip(),
            'email': str(row_data.get('email', '')).strip().lower()
        }
        #process password
        processed['password'] = generate_secure_password()
        # Process optional fields
        optional_fields = [
            'nationality', 'gender', 'date_of_birth', 
            'vulnerable', 'bio', 'city_of_residence'
        ]
        
        for field in optional_fields:
            value = row_data.get(field)
            processed[field] = '' if pd.isna(value) else str(value).strip()
        
        # Add metadata
        processed.update({
            'role': self.config.role or 'trainee',
            'batch_id': self.config.batch,
            'groups': [self.config.group_id] if self.config.group_id else [],
            'status': 'Accepted'
        })
        
        # Separate other info
        essential_fields = ['name', 'email', 'nationality', 'gender', 'date_of_birth', 'password',
                          'vulnerable', 'bio', 'city_of_residence', 'role', 
                          'batch_id', 'groups', 'status']
        processed['other_info'] = {
            k: v for k, v in processed.items() 
            if k not in essential_fields
        }
        
        return processed

    def _compile_results(self, total: int, successful: List, failed: List) -> Dict:
        """Compile final results"""
        status = 'completed' if not failed else 'partial_success' if successful else 'failed'
        
        return {
            'status': status,
            'total_processed': total,
            'successful': len(successful),
            'failed': len(failed),
            'successful_trainees': successful,
            'failed_trainees': failed,
            'errors': [{
                'row': t['row'],
                'email': t['email'],
                'error_message': t['error_message']
            } for t in failed],  # Add error details
            'batch': self.config.batch,
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'run_stage': self.config.run_stage,
                'role': self.config.role,
                'group_id': self.config.group_id
            }
        }

    def _create_record_error(self, row_data: Dict, row_num: int, error_msg: str) -> Dict:
        """Create standardized error response for a record"""
        return {
            'success': False,
            'row': row_num,
            'name': row_data.get('name', 'Unknown'),
            'email': row_data.get('email', 'Unknown'),
            'error_type': 'PROCESSING_ERROR',
            'error_message': error_msg,
            'trainee_data': row_data
        }

    def _create_error_response(self, error: Exception) -> Dict:
        """Create error response for batch failures"""
        return {
            'status': 'failed',
            'error': str(error),
            'error_type': 'BATCH_PROCESSING_ERROR',
            'batch': self.config.batch,
            'timestamp': datetime.now().isoformat(),
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'failed_trainees': [{
                'row': 0,
                'name': 'Batch Error',
                'email': 'N/A',
                'error_type': 'BATCH_PROCESSING_ERROR',
                'error_message': str(error),
                'trainee_data': {}
            }],
            'metadata': {
                'run_stage': self.config.run_stage,
                'role': self.config.role,
                'group_id': self.config.group_id
            }
        }

    async def _send_notifications(self, results: Dict) -> None:
        """Send email and webhook notifications"""
        try:
            # Always try to send webhook notification first if configured
            if self.webhook_service:
                try:
                    await self.webhook_service.notify_callback(results)
                    self.logger.info(
                        "Webhook notification sent successfully",
                        extra={
                            'notification_type': 'webhook',
                            'receiver_url': self.config.callback_url,
                            'batch_id': self.config.batch,
                            'status': results.get('status')
                        }
                    )
                except Exception as e:
                    self.logger.error(
                        f"Failed to send webhook notification",
                        extra={
                            'notification_type': 'webhook',
                            'receiver_url': self.config.callback_url,
                            'batch_id': self.config.batch,
                            'error': str(e)
                        }
                    )
            
            # Always try to send admin email if configured
            if self.email_service and self.config.admin_email:
                try:
                    # Prepare error details for failed trainees
                    error_details = []
                    for trainee in results.get('failed_trainees', []):
                        error_details.append({
                            'email': trainee.get('email', 'Unknown'),
                            'name': trainee.get('name', 'Unknown'),
                            'reason': f"{trainee.get('error_type', 'Unknown Error')}: {trainee.get('error_message', 'No message')}"
                        })
                    
                    # Always send admin summary email
                    await self.email_service.send_batch_summary_email(
                        admin_email=self.config.admin_email,
                        batch_id=self.config.batch,
                        total=results.get('total_processed', 0),
                        successful=results.get('successful', 0),
                        failed=results.get('failed', 0),
                        error_details=error_details
                    )
                    
                    self.logger.info(
                        f"Admin summary email delivered",
                        extra={
                            'notification_type': 'admin_summary',
                            'sender': self.sender_email,
                            'receiver': self.config.admin_email,
                            'batch_id': self.config.batch,
                            'status': 'delivered',
                            'processing_status': results.get('status')
                        }
                    )
                    
                    # Only send welcome emails for successful trainees
                    successful_trainees = results.get('successful_trainees', [])
                    if successful_trainees:
                        self.logger.info(
                            f"Starting trainee welcome emails",
                            extra={
                                'notification_type': 'trainee_welcome',
                                'sender': self.sender_email,
                                'batch_id': self.config.batch,
                                'trainee_count': len(successful_trainees)
                            }
                        )
                        
                        # Send welcome emails to successful trainees
                        for trainee in successful_trainees:
                            if trainee.get('email'):
                                try:
                                    await self.email_service.send_trainee_welcome_email(
                                        email=trainee['email'],
                                        username=trainee['email'],
                                        password=trainee.get('password', trainee['email']),
                                        login_url= self.config.login_url
                                    )
                                    
                                    self.logger.info(
                                        f"Trainee welcome email delivered",
                                        extra={
                                            'notification_type': 'trainee_welcome',
                                            'sender': self.sender_email,
                                            'receiver': trainee['email'],
                                            'batch_id': self.config.batch,
                                            'status': 'delivered'
                                        }
                                    )
                                except Exception as e:
                                    self.logger.error(
                                        f"Failed to send trainee welcome email",
                                        extra={
                                            'notification_type': 'trainee_welcome',
                                            'sender': self.sender_email,
                                            'receiver': trainee['email'],
                                            'batch_id': self.config.batch,
                                            'error': str(e)
                                        }
                                    )
                                
                except Exception as e:
                    self.logger.error(
                        f"Failed to send admin summary email",
                        extra={
                            'notification_type': 'admin_summary',
                            'sender': self.sender_email,
                            'receiver': self.config.admin_email,
                            'batch_id': self.config.batch,
                            'error': str(e)
                        }
                    )
            else:
                self.logger.warning(
                    "Email notifications skipped",
                    extra={
                        'reason': 'Email service not initialized' if not self.email_service else 'Admin email not provided',
                        'admin_email': self.config.admin_email,
                        'batch_id': self.config.batch
                    }
                )
                    
        except Exception as e:
            self.logger.error(
                f"Error in notification process",
                extra={
                    'batch_id': self.config.batch,
                    'sender': self.sender_email,
                    'error': str(e),
                    'notification_config': {
                        'webhook_url': self.config.callback_url if self.webhook_service else None,
                        'admin_email': self.config.admin_email if self.email_service else None
                    }
                }
            )

    def _cleanup_resources(self, error_step: str) -> None:
        """Clean up created resources in case of failure"""
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
            logger.error("Error during resource cleanup", extra={
                'error_step': error_step,
                'error': str(e)
            })