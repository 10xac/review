
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


class StrapiMethods:
    def __init__(self,root = 'dev-cms', ssmkey = 'dev/strapi/token'):
        self.api_url = "https://dev-cms.10academy.org"
        
        self.token = get_auth(ssmkey=ssmkey,
                 envvar='STRAPI_TOKEN',
                 fconfig=f'{cpath}/.env/{root}.json')
        
        

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
                # self.token['token']
                headers = {

                "Authorization": f"Bearer {token}", 

                "Content-Type": "application/json"}

            ).json()
        except Exception as e:
            print(e)
        return r
    
    

   
        
    
        

 

if __name__ == "__main__":
    obj = StrapiMethods()
    # table= "/api/title-trainees"
    
    table= "https://dev-cms.10academy.org/api/applicant-informations"
  