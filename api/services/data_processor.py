import pandas as pd
from fastapi import HTTPException
from typing import Dict, Union
from utils.gdrive import gsheet
from api.models.trainee import TraineeResponse

class DataProcessor:
    def __init__(self, config: Dict):
        self.config = config

    def get_applicant_data(self) -> pd.DataFrame:
        """
        Function to read application from google sheet. 
        Returns:
            df: dataframe with applicant information
        """
        if self.config.sheet_id:
            gd = gsheet(sheetid=self.config.sheet_id,
                       fauth='admin-10ac-service.json')
        else:
            raise HTTPException(status_code=400, detail="Sheet ID is required for batch processing")

        try:
            df = gd.get_sheet_df(self.config.sheet_name)
            print(f'------------{self.config.sheet_name} df.shape={df.shape}----')
            return df
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f'Could not obtain sheet for {self.config.sheet_name}: {str(e)}'
            )

    def process_single_trainee(self, trainee_data: Dict) -> Dict:
        """
        Process single trainee data from API request
        Args:
            trainee_data: Trainee information from the API request
        Returns:
            Dict: Processed trainee data
        """
        try:
            processed_data = {}
            
            # Process name
            name = getattr(trainee_data, 'name', '')
            if name:
                name = name.strip().title()
                name = name.replace('-', '').replace('.', '').replace('  ', ' ')
            processed_data['name'] = name

            # Process email
            email = getattr(trainee_data, 'email', '')
            if email:
                email = email.strip().lower()
            processed_data['email'] = email
            
            processed_data['password'] = getattr(trainee_data, 'password', '')
            if processed_data['password'] is None or processed_data['password'] == "":
                processed_data['password'] = processed_data['email']

            # Process other fields
            processed_data['nationality'] = getattr(trainee_data, 'nationality', '')
            processed_data['gender'] = getattr(trainee_data, 'gender', '')
            
            # Handle date_of_birth carefully
            date_of_birth = getattr(trainee_data, 'date_of_birth', None)
            if date_of_birth:
                if isinstance(date_of_birth, str):
                    try:
                        from datetime import datetime
                        parsed_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
                        processed_data['date_of_birth'] = parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        processed_data['date_of_birth'] = None
                elif hasattr(date_of_birth, 'strftime'):
                    processed_data['date_of_birth'] = date_of_birth.strftime('%Y-%m-%d')
                else:
                    processed_data['date_of_birth'] = None
            else:
                processed_data['date_of_birth'] = None

            processed_data['vulnerable'] = getattr(trainee_data, 'vulnerable', '')
            processed_data['status'] = getattr(trainee_data, 'status', 'Accepted')
            
            if processed_data['status'] is None or processed_data['status'] == "":
                processed_data['status'] = 'Accepted'

            # Add config information
            processed_data['role'] = self.config.role
            if processed_data['role'] is None or processed_data['role'] == "":
                processed_data['role'] = 'trainee'

            # Handle batch_id
            if self.config.batch is None or self.config.batch == "":
                processed_data['batch_id'] = []
            else:
                processed_data['batch_id'] = [self.config.batch]

            # Handle groups
            if self.config.group_id is None or self.config.group_id == "":
                processed_data['groups'] = []
            else:
                processed_data['groups'] = [self.config.group_id]

            # Validate required fields
            required_fields = ['name', 'email']
            missing_fields = [field for field in required_fields if not processed_data.get(field)]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            return processed_data
            
        except Exception as e:
            return TraineeResponse.error_response(
                error_type="DATA_PROCESSING_ERROR",
                error_message=str(e),
                error_location="trainee_data_processing",
                error_data={"input_data": trainee_data}
            )

    @staticmethod
    def change_name_fullname(row: pd.Series) -> str:
        """
        Function to change names to full name. 
        Args: 
            row: row contains first name and last name
        Returns:
            fname: returns full name
        """
        fname = row['firstname'].strip().title()
        lname = row['familyname'].strip().title()
        lenstring = fname.split(" ")
        lname_words = lname.split(" ")
        if len(lenstring) < 2:
            fullname = fname + " " + lname_words[0]
            return fullname
        else:
            return fname

    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Function to preprocess trainee information from dataframe 
        Args:
            df: Input dataframe
        Returns:
            df: Processed dataframe
        """
        to_standardize_name = ['Name', 'Full Name', 'fullname']
        country_or_nationality = ['Nationality', 'Country']
        
        # Create a dictionary to map old column names to a new name
        rename_dict = {col: 'Name' for col in df.columns if col.strip() in to_standardize_name}
        sec_rename_dict = {col: 'Country' for col in df.columns if col in country_or_nationality}
        
        df.rename(columns=rename_dict, inplace=True)
        df.rename(columns=sec_rename_dict, inplace=True)
        
        df['Batch'] = self.config.batch
        df['Name'] = df['Name'].apply(lambda x: x.strip().title())
        df['Name'] = df['Name'].apply(lambda x: x.replace('-', '').replace('.', '').replace('  ', ' '))
        df['Email'] = df['Email'].apply(lambda x: x.strip().lower())
        
        return df

    def prepare_applicants(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Function to prepare applicant data for insertion from dataframe
        Args:
            df: Input dataframe
        Returns:
            df: Prepared dataframe
        """
        df = df.replace('', 'null')
        gender_cols = ['Gender', 'gender']
        rename_dict = {col: 'gender' for col in df.columns if col in gender_cols}
        df.rename(columns=rename_dict, inplace=True)

        df.rename(columns={'Name': 'name', 'Email': 'email'}, inplace=True)
        if 'Date of Birth' in df.columns:
            df['Date of Birth'] = pd.to_datetime(df['Date of Birth'])
        
        if 'Section' in df.columns:
            df = df[df['Section'] == 'A']
            
        df['role'] = self.config.role
        df['Batch'] = int(self.config.batch)
        return df


    def find_duplicates(self, df: pd.DataFrame) -> Dict:
        """
        Find duplicate entries in the trainee data based on name and email
        Args:
            df: Input dataframe with trainee data
        Returns:
            Dict: Information about duplicate entries if found
        """
        # Create a clean key for comparison (lowercase, trimmed)
        df['comparison_key'] = df.apply(
            lambda x: (
                str(x['name']).lower().strip(),
                str(x['email']).lower().strip()
            ),
            axis=1
        )
        
        # Find duplicates
        duplicates = df[df['comparison_key'].duplicated(keep=False)]
        
        if len(duplicates) > 0:
            # Group duplicates and format the result
            duplicate_groups = duplicates.groupby('comparison_key').apply(
                lambda x: x[['name', 'email']].to_dict('records')
            ).to_dict()
            
            return {
                "found": True,
                "count": len(duplicates),
                "entries": duplicate_groups
            }
        
        return {"found": False, "count": 0, "entries": {}}


    def process_batch_data(self) -> pd.DataFrame:
        """
        Process the entire batch data pipeline
        Returns:
            df: Processed dataframe ready for insertion
        """
        df = self.get_applicant_data()
        df = self.process_dataframe(df)
        df = self.prepare_applicants(df)
        
        # Check for duplicates
        duplicates = self.find_duplicates(df)
        if duplicates["found"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": f"Found {duplicates['count']} duplicate entries",
                    "duplicates": duplicates['entries']
                }
            )
        
        return df