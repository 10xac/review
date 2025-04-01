import pandas as pd
from fastapi import HTTPException
from typing import Dict, Union
from utils.gdrive import gsheet

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

        # Process other fields
        processed_data['nationality'] = getattr(trainee_data, 'nationality', '')
        processed_data['gender'] = getattr(trainee_data, 'gender', '')
        processed_data['date_of_birth'] = getattr(trainee_data, 'date_of_birth', None)
        processed_data['vulnerable'] = getattr(trainee_data, 'vulnerable', '')
        processed_data['status'] = getattr(trainee_data, 'status', 'Accepted')

        # Add config information
        processed_data['role'] = self.config.role
        processed_data['batch_id'] = int(self.config.batch)

        # Validate required fields
        required_fields = ['name', 'email', 'nationality', 'gender', 'date_of_birth']
        print(f"processed_data: {processed_data}")
        missing_fields = [field for field in required_fields if not processed_data.get(field)]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )

        return processed_data

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

    def process_batch_data(self) -> pd.DataFrame:
        """
        Process the entire batch data pipeline
        Returns:
            df: Processed dataframe ready for insertion
        """
        df = self.get_applicant_data()
        df = self.process_dataframe(df)
        df = self.prepare_applicants(df)
        return df 