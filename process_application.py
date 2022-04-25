
from enum import unique
import json
import sys, os
from types import new_class
import pandas as pd
from numpy import mat
curdir = os.path.dirname(os.path.realpath(__file__))
print(curdir)
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)

from secret import get_auth

import math
import datetime
from get_applicants import process_dataframe, get_applicant_data
from strapi_methods import StrapiMethods as sm

class ProcessApplication:
    
    def __init__(self):
        self.api_url = "https://dev-cms.10academy.org"
        
        self.token = get_auth(ssmkey='dev/strapi/token',
                 envvar='STRAPI_TOKEN',
                 fconfig=f'{cpath}/.env/Strapi_token.json')
        
        print("Writing gspread config to /.env/Strapi_token.json")
        
    def prepare_applicants  (self):

        df = process_dataframe()
        df = df.replace('', 'null')
        user_df = df[['email','firstname']]
        user_df.rename(columns = {'firstname':'name'}, inplace = True)
        user_df['role']= "applicant"
        return user_df
    def insert_all_users (self,table):
        
        df = ProcessApplication.prepare_applicants(self)
        result = df.to_json(orient="records", date_format = 'iso')
       
        for data in json.loads(result):
            sm.insert_data(self,data,table, token = self.token['token'])
        
        print("All records are inserted") 
        
        
    def select_from_trainees(self):
        dic_list= []
        
        table= f"https://cms.10academy.org/api/all-users?pagination[page]=0&pagination[pageSize]=1042"
        dic = sm.fetch_data(self, table,self.token['token'])
        df_0 = pd.json_normalize(dic['data'])
        
        pageCount = dic['meta']['pagination']['pageCount']
        dic_list.append(df_0)
        
       
        for i in range (pageCount):
            
            if i  == 0:
                continue
            else:
                
                table= f"https://dev-cms.10academy.org/api/all-users?pagination[page]={i+1}&pagination[pageSize]=100"
                dic = sm.fetch_data(self, table,self.token['token'])
                df = pd.json_normalize(dic['data'])
                dic_list.append(df)
        return dic_list
    
    
    def process_with_question_type(self):
        graduation =  "When is your graduation date? Put your expected graduation date if you are still studying (Note: Applicants whose graduation date is between 1 Jan 2020 and 30 April 2022 are likely to be prioritized - a proof will be asked for at a later stage of the process)"
        user_list = ProcessApplication.select_from_trainees(self)
        
        merged = pd.concat(user_list)# from strapi
        print(merged.columns)
   
        
        
if __name__ == "__main__":
    obj = ProcessApplication()
    
    # table= "https://dev-cms.10academy.org/api/all-users"
    obj.process_with_question_type()