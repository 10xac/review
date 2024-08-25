import numpy as np
import os, sys
import pandas as pd
import time
import uuid
import json
#
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
print(cpath)
if not cpath in sys.path:
    sys.path.append(cpath)

#  
from review_scripts.communication_manager import CommunicationManager
from review_scripts.strapi_graphql import StrapiGraphql
from review_scripts.strapi_methods import StrapiMethods
from utils.gdrive import gsheet


### change this for different run configurations
# from run_configs import u2j_trainee_config
# from run_configs import  kiam_batch2_trainee_config
from run_configs import u2j_batch2_trainee_config

# def training_mapper(run_stage):


class TraineeInformationProcesssor:
    def __init__(self, Kwargs = None):
        if "configs" in Kwargs:
            self.configs = Kwargs["configs"]
        else:
            self.configs = u2j_batch2_trainee_config #kiam_batch2_trainee_config
        self.run_stage = self.configs.run_stage
        self.sg = StrapiGraphql(run_stage=self.configs.run_stage)
        self.sm = StrapiMethods(run_stage=self.configs.run_stage)
        self.cm = CommunicationManager()
    

    def insert_user(self, user_data):
        """
        A function to insert user data into the database.

        Parameters:
            user_data (dict): A dictionary containing user data with keys 'email' and 'name'.

        Returns:
            int: The user ID of the newly created user.
        """
        print("inserting user.....", user_data)
        result_json = self.cm.create_user(self.sg, user_data)
        print("result json", result_json)
        try:
            user_id = result_json['data']['register']['user']['id']
        except:
            print("ERROR: Could not create user....................", user_data)
            user_id = 0
       
        return  user_id 
    def get_applicant_data(self):
        """
        Function to read application from google sheet. 
        Args: 
            sid_application: sheet id for the application information 
        Returns:
            df: dataframe
        """

        if self.configs.sheet_id:
            gd = gsheet(sheetid=self.configs.sheet_id,
                        fauth='admin-10ac-service.json')
        else:

            gd = gsheet(sheetid="1mG8uNDxaDfNq-iRi-_-mgsz5rArkrMPAXtV8IR53xXM",
                    fauth='admin-10ac-service.json')
   

        try:
            df = gd.get_sheet_df(self.configs.sheet_name)

            # print(df.head())
            print(f'------------{self.configs.sheet_name} df.shape={df.shape}----')

        except Exception as e:
            print(f'ERROR: Could not obtain sheet for {self.configs.sheet_name}', e)

        return df
    def change_name_fullname(self, row):
        """
        Function to change names to full name . 
        Args: 
            row: row containes first name and last name
        Returns:
            fname: returns full name
        """
        fname = row['firstname'].strip().title()
        lname = row['familyname'].strip().title()
        lenstring = fname.split(" ")
        lname_words = lname.split(" ")
        if len(lenstring) < 2:
            fullname = fname+" "+lname_words[0]
            return fullname
        else:
            return fname
    def process_dataframe(self):

        """
        Function to preprocess trainee information  
       
        Returns:
            df: dataframe
        """

        app_df = self.get_applicant_data()
        df = app_df
        to_standardize_name = ['Name', 'Full Name', 'fullname']
        contry_or_nationality  = ['Nationality', 'Country']
        # Create a dictionary to map old column names to a new name
        rename_dict = {col: 'Name' for col in df.columns if col in to_standardize_name}
        sec_rename_dict= {col: 'Country' for col in df.columns if col in contry_or_nationality}
        df.rename(columns=rename_dict, inplace=True)
        df.rename(columns=sec_rename_dict, inplace=True)
       
    
        df['Batch'] = self.configs.batch

        df['Name'] = df['Name'].apply(lambda x: x.strip().title())
        ## remove -. from name in df 
        df['Name'] = df['Name'].apply(lambda x: x.replace('-', '').replace('.', '').replace('  ', ' '))

        df['Email'] = df['Email'].apply(lambda x: x.strip().lower())
        return df
    def prepare_applicants(self):

        df = self.process_dataframe()
        df = df.replace('', 'null')
        gender = ['Gender', 'gender']
        rename_dict= {col: 'gender' for col in df.columns if col in gender}
        df.rename(columns=rename_dict, inplace=True)

        user_df = df[['Email', 'Name', 'Country', 'gender']]
        user_df.rename(columns={'Name': 'name', 'Email': 'email'}, inplace=True)
        user_df['role'] = self.configs.role
        user_df['Batch'] = int(self.configs.batch)
        return user_df
    
    def process_user_and_alluser_insertion(self):
        df = self.prepare_applicants()
        # df = df[81:]
        # Calculate the number of chunks needed
        num_chunks = (len(df) + 19) // 20  # This ensures that even the last chunk less than 50 rows is processed

        for chunk in range(num_chunks):
            # Process each chunk of 50 rows
            start_index = chunk * 20
            end_index = start_index + 20
            df_chunk = df.iloc[start_index:end_index]  # Get the chunk

            for i, row in df_chunk.iterrows():
                res_dict = {
                    "name": row['name'],
                    "email": row['email'],
                    "role": row['role'],
                    "batch": row['Batch'],
                }
                userId = self.insert_user(res_dict)
                # if userId == 0:
                    # continue
                # res_dict['userId'] = userId
                # res = self.cm.insert_all_users(self.sg, res_dict)
                # print(res)

            # Print the chunk processing status
            print(f"Processed rows {start_index + 1} to {end_index}")

            # If not the last chunk, pause for 5 minutes
            if chunk < num_chunks - 1:
                print("Pausing for 5 minutes...")
                time.sleep(20)
            
        print("All records have been inserted successfully")
    

    ########################################################
    ### Insertion of profile information 
    def extract_last_name(self, name):
        parts = name.split()
        return ' '.join(parts[1:]) if len(parts) > 1 else ''


    def select_batch_users_from_allusers(self):
        """
        Function to preprocess trainee information  
       
        Returns:
            df: dataframe
        """
      
        batch = int(self.configs.batch)
        req_params = {"batch":batch, "role":self.configs.role}
        result_json = self.cm.read_all_users(self.sg, req_params)
        df = pd.json_normalize(result_json['data']['allUsers']['data'])
        df.rename(columns={"attributes.name": "name", "attributes.email": "Email",
                    "attributes.Batch": "batches", 'id':'all_user'}, inplace=True)
       
        df = df.drop(columns=['name'])
        return df


    def process_profile_information_insertion(self):
        df = self.prepare_applicants()
        adf = self.select_batch_users_from_allusers()
        adf.rename(columns={"Email": "email"}, inplace=True)
        ddf = df.merge(adf, on="email", how="left")
        ddf['role'] = "trainee"

        ddf['last_name'] = ddf['name'].apply(self.extract_last_name)
        ddf['first_name'] = ddf['name'].str.split(' ').str[0]

        # Determine the number of chunks needed
        num_chunks = (len(ddf) + 49) // 50  # Rounds up to include all records

        for chunk in range(num_chunks):
            start_index = chunk * 50
            end_index = start_index + 50
            df_chunk = ddf.iloc[start_index:end_index]  # Get the current chunk

            for i, row in df_chunk.iterrows():
                print("processing..................", row['email'])
                dict_res = {
                    "firstName": row['first_name'],
                    "surName": row['last_name'],
                    "nationality": row['Country'],
                    "gender": row['gender'],
                    "email": row['email'],
                    "alluser": row['all_user']
                }
                res = self.cm.insert_profile_information(self.sg, dict_res)
                print(res)

            # Print chunk processing status
            print(f"Processed rows {start_index + 1} to min({end_index}, {len(ddf)})")

            # If not the last chunk, pause for 5 minutes
            if chunk < num_chunks - 1:
                print("Pausing for 5 minutes...")
                time.sleep(300)  # Sleep for 300 seconds or 5 minutes

        print("All records have been inserted successfully")


    def insert_group(self):
        """
        Function to insert users to group table. 
        
        Returns:
           
        """

        adf =self.select_batch_users_from_allusers()
   
        adf.rename(columns={'all_user':'all_users','name':'Name'}, inplace=True)
        ids = adf['all_users'].to_list()
  
        table = "groups"
      
        batch_name = "B"+str(self.configs.batch)#+ "-"+ "w0"
        data={'Name':batch_name,'all_users':ids}

        r = self.sm.insert_data(data, table)
        print(r)
    
    ###################################################################
    ### To insert traineees
    def generate_uuid(self):
        """Generate a unique UUID."""
        uuid_value = uuid.uuid4()

        return str( uuid_value )
    def get_batch (self):
        """
            Function to get current batch from strapi graphql

        Args:
            Self.batch (Int): Number that represent current batch 

        Returns:
            Strapi Id of the imputed batch 
        """
    
        batch = int(self.configs.batch)
        batch_json = self.cm.read_batch_information(self.sg, {'batch': batch})
        batchdf =  pd.json_normalize(batch_json['data']['batches']['data'])
        batch  = batchdf[batchdf['attributes.Batch']==batch]
        return int(batch['id'])
    
    def process_for_trainee_submission(self):
        batch = self.get_batch()
        adf = self.select_batch_users_from_allusers()
        adf.rename(columns={"Email":"email"}, inplace=True)
        adf = adf[['all_user','email']]
 
        adf['batch'] =  str(batch)
        ### create UUID for all trainee
        adf['trainee_id'] = adf['email'].apply(lambda x: self.generate_uuid())
        adf['Status'] ="Accepted"
        
        print("INFO:Total number of newly accepted with trainee ",adf.shape)
        result = adf.to_json(orient="records", date_format = 'iso')
        
        # url = f"https://{self.root}.10academy.org/api/trainees"
        url = "trainees"

        for single in json.loads(result):
            print(single)
            r= self.sm.insert_data(single,url)
            print(r)

        print("All records have been inserted successfully")

