import os, sys
import pandas as pd
#
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
print(cpath)
if not cpath in sys.path:
    sys.path.append(cpath)

#  
from review_scripts.communication_manager import CommunicationManager

from review_scripts.strapi_graphql import StrapiGraphql
from utils.gdrive import gsheet

### change this for different run configurations
from run_configs import u2j_staff_config


class StaffInformationProcessor:
    def __init__(self):
        self.configs = u2j_staff_config
        self.run_stage = self.configs.run_stage
        self.sg = StrapiGraphql(run_stage=self.configs.run_stage)
        self.cm = CommunicationManager()
    def create_new_batch(self):
        batch_params  = {
        "batch": self.configs.batch,
        "class_link": self.configs.class_link,
        "communication_link": self.configs.communication_link,
        "additional_info": self.configs.additional_info
        }
        ### create batch 
        res_json = self.cm.create_new_batch(self.sg, batch_params)
        return res_json
    def get_staff_data(self):
        """
        Function to read staff data from specified sheet from google sheet. 
        Args: 
            sid_application: sheet id for the staff information 
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
    def insert_user(self, user_data):
        """
        A function to insert user data into the database.

        Parameters:
            user_data (dict): A dictionary containing user data with keys 'email' and 'name'.

        Returns:
            int: The user ID of the newly created user.
        """
        result_json = self.cm.create_user(self.sg, user_data)
        try:
            user_id = result_json['data']['register']['user']['id']
        except:
            print("ERROR: Could not create user....................", user_data)
            user_id = 0
       
        return  user_id 
    def insert_staff_all_users(self):
        """
        Function to insert staff to user and all user table. 
        
        Returns:
            None
        """

        staff_df = self.get_staff_data()
        df = staff_df
        ### Full Name of full name exist in dataframe.columns rename name column
        to_standardize_name = ['Name', 'Full Name', 'fullname']
        # Create a dictionary to map old column names to a new name
        rename_dict = {col: 'name' for col in df.columns if col in to_standardize_name}

        # Rename the columns using the dictionary
        df.rename(columns=rename_dict, inplace=True)
        df.rename(columns={'Name': 'name', #'Role': 'role',
                  "Email": "email"}, inplace=True)
        

        for i, row in df.iterrows():
            res_dict = {
                "name": row['name'],
                "email": row['email'],
                "role": self.configs.role,
                "batch": int(self.configs.batch),
            }
        
            userId = self.insert_user( row)
            if userId == 0:
                continue
            res_dict['userId']= userId
            print(res_dict)
            res = self.cm.insert_all_users(self.sg, res_dict)
            print(res)
        print("All records are inserted")
    

    def get_batch_id(self):
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
    
    def select_users_from_allusers(self):
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
    def insert_reviewers(self):
        """
        Function to insert users to reviewers table. 
        
        Returns:
           
        """
        batch = self.get_batch_id()
        df =self.select_users_from_allusers()
        df.rename(columns={'id':'all_user','Batch':'batches','email':'Email'}, inplace=True)
        df= df[['all_user', 'Email']]
    
        df['batches']= batch


        for i, row in df.iterrows():
            res = self.cm.create_reviewer(self.sg, row)
            print(res)
        print("All records are inserted")

    def create_group_for_staff(self):
        "!!!!!!! Don't run as it is check for the default value"
        res = self.cm.read_batch_specific_reviewers(self.sg, self.configs.batch)
        batch_specific_staff_id =  []
        for i in res['data']['reviewers']['data']:
            batch_specific_staff_id.append(i['id'])

        group_params = {
            "alluserIDS": batch_specific_staff_id, 
        }
        res_json =  self.cm.create_group_for_staff(self.sg, group_params)
        print(res_json)


    ##################### Prefeerence
    def extract_user_info(self, json_data):
        user_info = []
        for record in json_data:
            try:
                user_id = record['attributes']['user']['data']['id']
                user_email = record['attributes']['user']['data']['attributes']['email']
                user_info.append({"user_id":user_id, "user_email":user_email})
            except KeyError as e:
                print(f"Missing key: {e}")
                continue
        return user_info
    def insert_user_preference (self):
        res_json =  self.cm.read_all_users(self.sg, {"batch":self.configs.batch, 
                                                     "role":self.configs.role})
        user_details = self.extract_user_info(res_json['data']['allUsers']['data'])
        staff_df = self.get_staff_data()
        staff_df.rename(columns={'Full Name': 'name', 'Email': 'user_email'}, inplace=True)
        df = pd.DataFrame(user_details)
        all_df = pd.merge(staff_df, df, on='user_email', how='left')

        default_setting =  {"batch": self.get_batch_id(),"batchID": self.configs.batch}

        for i, row in all_df.iterrows():
            
            variables= {"main_user_id":row['user_id'],
                        "email": row['user_email'],
                        "defaultSettings":default_setting}
            res = self.cm.create_user_preference(self.sg, variables)
            print (res)
       






if __name__ == "__main__":
    sm = StaffInformationProcessor()
    print(sm.create_group_for_staff())