
from numpy import int64
import pandas as pd
import requests
import json
import os,sys
import numpy as np
curdir = os.path.dirname(os.path.realpath(__file__))
print(curdir)
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)

from secret import get_auth
from get_applicants import process_dataframe

class StrapiMethods:
    def __init__(self):
        self.api_url = "https://dev-cms.10academy.org"
        
        self.token = get_auth(ssmkey='dev/strapi/token',
                 envvar='STRAPI_TOKEN',
                 fconfig=f'{cpath}/.env/Strapi_token.json')
        
        print("Writing gspread config to /.env/Strapi_token.json")

    def fetch_data(self,table, token):
       
        r = requests.get(table,headers = {

                        "Authorization": f"Bearer {token}", 

                        "Content-Type": "application/json"})
        return r.json()
    
                
    def update(self,table, id, params, token):
        
        r = requests.put(table+ str(id),
        data=json.dumps({
           "data":params
        }),
        headers={
            "Authorization": f"Bearer {token}", 
            'Content-Type': 'application/json'
        })
        
        
    def insert_data (self,data,table,token ):
       
        try:
            r = requests.post(

                table, 

                data = json.dumps({"data":data}),

                headers = {

                "Authorization": f"Bearer {token}", 

                "Content-Type": "application/json"}

            ).json()
        except Exception as e:
            print(e)
    
    

        
    def prepare_applicants  (self,table):

        df = process_dataframe()
        df = df.replace('', 'null')
        
        # for i in df['date_of_birth']:
        #     print(type(i))
        df['time_stamp'] = pd.to_datetime(df['time_stamp'], errors='coerce')
        df['graduation_date'] = pd.to_datetime(df['graduation_date'], errors='coerce')
        df['date_of_birth']= pd.to_datetime(df["date_of_birth"], errors = 'coerce')
      
        result = df.to_json(orient="records", date_format = 'iso')
       
        for data in json.loads(result):
            # python_proficiency','sql_proficiency', 'statistics_proficiency', 'algebra_proficiency','project_compeleted'
            data['python_proficiency'] = int(data['python_proficiency'])
            data['sql_proficiency'] = int(data['sql_proficiency'])
            data['statistics_proficiency'] = int(data['statistics_proficiency'])
            data['algebra_proficiency'] = int(data['algebra_proficiency'])
            
            
            
            StrapiMethods.insert_data(self,data,table)
            
        
        print("All records are inserted") 
        
    
        

 

if __name__ == "__main__":
    obj = StrapiMethods()
    # table= "/api/title-trainees"
    # # print(obj.organize_data())
    # print(obj.prepare_jobs("/api/trainee-jobs"))
    # print(obj.prepare_for_job_Trainee(table))
    # obj.prepare_competency()
    # print(obj.fetch_data("/api/trainee-jobs"))
    table= "https://dev-cms.10academy.org/api/applicant-informations"
    obj.prepare_applicants(table)