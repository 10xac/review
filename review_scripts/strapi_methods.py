
from numpy import int64
import pandas as pd
import requests
import json
import os,sys
import numpy as np

# from pathfig import *
import os, sys
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
print(cpath)
if not cpath in sys.path:
    sys.path.append(cpath)
from utils.secret import get_auth, lambda_friendly_path
import utils.config as config


class StrapiMethods:
    def __init__(self, **kwargs):

        run_stage =  config.strapi.stage
        root = config.strapi.root
        ssmkey = config.strapi.ssmkey     
        self.api_url = f"https://{root}.10academy.org"
       
        self.ssmkey = ssmkey
        
        self.token = get_auth(ssmkey,
                             envvar='STRAPI_TOKEN',
                             fconfig=lambda_friendly_path(f'.env/{root}.json'))

        self.headers = {"Authorization": f"Bearer {self.token}"}

        

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
        
        
    def insert_data (self,data, table):
        table = self.api_url +"/api/"+ table
        print(table)
        try:
            r = requests.post(

                table, 

                data = json.dumps({"data":data}),
                # self.token['token']
                headers = {

                "Authorization": f"Bearer {self.token}", 

                "Content-Type": "application/json"}

            ).json()
        except Exception as e:
            print(e)
        return r
    
  