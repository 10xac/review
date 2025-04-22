import boto3
from botocore.exceptions import ClientError
import logging
from typing import List, Dict, Optional
import asyncio
from functools import wraps

def async_wrap(func):
    @wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return run

class EmailService:
    def __init__(self, region_name: str = "us-east-1", source_email: str = None):
        """
        Initialize the email service with AWS SES
        Args:
            region_name: AWS region name
            source_email: Verified email address to send from
        """
        self.client = boto3.client('ses', region_name=region_name)
        self.source_email = source_email
        self.logger = logging.getLogger(__name__)

    @async_wrap
    def send_trainee_welcome_email(self, email: str, username: str, password: str, login_url: str) -> bool:
        """
        Send welcome email to newly registered trainee
        Args:
            email: Trainee's email address
            username: Trainee's username
            password: Trainee's password
            login_url: URL where trainee can login
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        subject = "Welcome to Our Training Platform"
        body = f"""
        Dear Trainee,

        Your account has been successfully created on our training platform.

        Here are your login credentials:
        Username: {username}
        Password: {password}

        You can login at: {login_url}

        Please change your password after your first login.

        Best regards,
        The Training Team
        """
        return self._send_email(email, subject, body)

    @async_wrap
    def send_batch_summary_email(self, admin_email: str, batch_id: int, 
                               total: int, successful: int, failed: int, 
                               error_details: Optional[List[Dict]] = None,
                               successful_details: Optional[List[Dict]] = None,
                               is_mock: bool = False) -> bool:
        """
        Send batch processing summary email to administrator
        Args:
            admin_email: Administrator's email address
            batch_id: Batch identifier
            total: Total number of records processed
            successful: Number of successful registrations
            failed: Number of failed registrations
            error_details: List of errors encountered
            successful_details: List of successful trainees with credentials if mock mode
            is_mock: Whether this is a mock batch
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        subject = f"Batch Processing Summary - Batch {batch_id}"
        
        success_rate = (successful / total * 100) if total > 0 else 0
        
        body = f"""
        Dear Administrator,

        The batch processing for Batch {batch_id} has been completed.

        Processing Summary:
        - Total Records: {total}
        - Successfully Processed: {successful}
        - Failed: {failed}
        - Success Rate: {success_rate:.2f}%

        {self._format_error_details(error_details) if error_details else ""}

        {self._format_successful_details(successful_details) if successful_details and is_mock else ""}

        Best regards,
        System Administrator
        """
        return self._send_email(admin_email, subject, body)

    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email using Amazon SES
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.source_email:
            self.logger.error("Source email not configured")
            return False

        try:
            response = self.client.send_email(
                Source=self.source_email,
                Destination={
                    'ToAddresses': [to_email]
                },
                Message={
                    'Subject': {
                        'Data': subject
                    },
                    'Body': {
                        'Text': {
                            'Data': body
                        }
                    }
                }
            )
            self.logger.info(f"Email sent successfully to {to_email}", 
                           extra={'message_id': response['MessageId']})
            return True
            
        except ClientError as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending email to {to_email}: {str(e)}")
            return False

    def _format_error_details(self, error_details: List[Dict]) -> str:
        """Format error details for email body"""
        if not error_details:
            return ""
            
        error_text = "\nError Details:\n"
        for error in error_details:
            error_text += f"- {error.get('email', 'Unknown')}: {error.get('reason', 'Unknown error')}\n"
        return error_text 

    def _format_successful_details(self, successful_details: List[Dict]) -> str:
        """Format successful trainee details for email body"""
        if not successful_details:
            return ""
            
        details_text = "\nSuccessful Trainees:\n"
        for trainee in successful_details:
            details_text += f"- {trainee.get('name', 'Unknown')} ({trainee.get('email', 'Unknown')})\n"
            if 'credentials' in trainee:
                details_text += f"  Username: {trainee['credentials']['username']}\n"
                details_text += f"  Password: {trainee['credentials']['password']}\n"
        return details_text 