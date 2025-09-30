
import json
import os
import sys
import datetime
import re
import numpy as np
import pandas as pd
#
from review_scripts.strapi_graphql import StrapiGraphql
from review_scripts.strapi_methods import StrapiMethods

from review_scripts.gdrive import gsheet

class InsertUserSpecial_challenge:
    def __init__(self, run_stage = "dev-cms", batch= None, role="trainee") -> None:

        self.sg = StrapiGraphql(run_stage)
        self.sm = StrapiMethods(run_stage)
        
        self.batch = batch
        self.role = role

    def get_accepted_trainee (self, sid = "1c82RJ9jn_ltOXd31QIy_ajohuJs5W88QXTOREVAmIHw"):

        gst = gsheet(sheetid=sid,fauth='admin-10ac-service.json') 
        dfg = gst.get_sheet_df("Form responses 1")
        df = dfg.T
        df = df.rename(columns={ 'What is your email?':'email', 'What is your full name? ':'name',
            'What is your batch? ':'batch_string',
            'From the mentioned challenges, which one are you interested in?':"interested",
            'What\'s your availability from 23 Jan to 31 Jan':"availability"})
        df['Batch']= df['batch_string'].apply(lambda x:int(re.sub(r"\D", "", x)) )
        
        df['email'] = df['email'].apply(lambda x: x.strip().lower())
        df['role']=self.role
       
        return  df[df['Batch']==self.batch]
    
    def select_applicants_from_allusers(self):
        query = """ query getAllUser($batch:Int,$role:String){
                allUsers(pagination:{start:0, limit:2000} filters:{Batch:{eq:$batch}, role:{eq:$role}}){
                    meta{
                    pagination{
                        total
                    }
                    }
                    data{
                    id
                    attributes{
                        name
                        email
                        Batch
                    }
                    }
                }
                }
            """

        result_json = self.sg.Select_from_table(query=query, variables={"batch":self.batch, "role": self.role})

        df = pd.json_normalize(result_json['data']['allUsers']['data'])
        df.rename(columns={"attributes.name": "name", "attributes.email": "Email",
                    "attributes.Batch": "batches", 'id':'all_user'}, inplace=True)
       
        df = df.drop(columns=['name'])
        return df
    def insert_user(self, df):
        all_ids= []
        allemail =[]
        for indx, items in df.iterrows():
        
                email = items['email']
                uname = items['name']
                # all_user_id = items['all_users']
                print(email, uname,)
                
                query = """mutation createUser($username:String!,$email:String!) { register(input: { username: $username, email: $email, password: $email } ) { user { id username email }  } }"""
                variables = {"username": uname, "email":email}
                result_json = self.sg.Select_from_table(query=query, variables= variables)
                print( result_json)
                all_ids.append(result_json['data']['register']['user']['id'])
                allemail.append(result_json['data']['register']['user']['email'])
        
        return all_ids, allemail

    def insert_all_users(self, df):
        table =f"https://{self.root}.10academy.org/api/all-users"
        # result = df.to_json(orient="records", date_format='iso')

        for i,row in df.iterrows():
            row_dict = {
                    "name":row['name'],
                    "email":row['email'],
                    "role":row['role'],
                    "Batch":row['Batch'],
                    "user":row['user'],
            }
           
            r = self.sm.insert_data(row_dict, table, self.sm.token['token'])
            print(r)
      
        print("All records are inserted")


    def insert_reviewers(self):
        df =self.select_applicants_from_allusers()
        to_exclude = ['brianodhiambo530@gmail.com','rahelweldegebriel2120@gmail.com','smlnegash@gmail.com',
                        'alaroabubakarolayemi@gmail.com','s.mwikali.muoki@gmail.com','lotomej12@gmail.com',
                        'natananshiferaw@gmail.com']
        
      
        df= df[~df['Email'].isin(to_exclude)]
        print(df.columns)
        df.rename(columns={'id':'all_user','Batch':'batches','email':'Email'}, inplace=True)
      
        table = f"https://{self.root}.10academy.org/api/reviewers"
        result = df.to_json(orient="records", date_format='iso')
           

        for data in json.loads(result):
            print(data)
            r = self.sm.insert_data(data, table, self.sm.token['token'])
            print(r)
            # break
        print("All records are inserted")

    def insert_group(self):
        adf =self.select_applicants_from_allusers()
        
        ids = adf['all_users'].to_list()
        table = f"https://{self.root}.10academy.org/api/groups"
      
        batch_name = "B"+str(self.batch)
        data={'Name':batch_name,'all_users':ids}

        r = self.sm.insert_data(data, table, self.sm.token['token'])
        print(r)