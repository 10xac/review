


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



class StrapiGraphql():
    def __init__(self, root='stage-cms', ssmkey="dev/strapi/token"):
        self.apiroot = f"https://{root}.10academy.org/graphql" 
        self.ssmkey = ssmkey
        
        self.token= get_auth(ssmkey,envvar='STRAPI_TOKEN',
                fconfig=f'{cpath}/.env/{root}.json')
        self.headers = {"Authorization": f"Bearer {self.token['token']}"}
      
    
    
    
    
    def get_token(self):
       
        return get_auth(ssmkey=self.ssmkey, fconfig=f'{cpath}/.env/Strapi_token.json')
        
        
        
    def insert_table (self, query, variables):
        """

        Args:
            query (String): You can write mutation graphql query to insert 
            variables (stirng ): Values of each attributes needs to be inserted 

        Raises:
            Exception: _description_

        Returns:
            result_json (Json): Response for your request 
        """
        # use CreateTablename() Mutation query 
        
        request = requests.post(self.apiroot, json={'query': query, 'variables': variables}, headers=self.headers)
        if request.status_code == 200:
            r =  request.json()
            result_json= json.dumps(r, indent=2)
            
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(
                    request.status_code, query))
        
        return result_json
    
    def Select_from_table (self,query, variables):
        
        """

        Args:
            query (String): You can write query graphql query to select from table
            variables (stirng ): values if you have specific filter 

        Raises:
            Exception: _description_

        Returns:
            result_json (Json): Response for your request 
        """
        
        # Use query to select from table  
        if variables ==None:
            request = requests.post(self.apiroot, json={'query': query}, headers=self.headers)
            if request.status_code == 200:
                r =  request.json()
                # result_json= json.dumps(r, indent=2)
                
            else:
                raise Exception("Query failed to run by returning code of {}. {}".format(
                        request.status_code, query))
            
            return r
        else:
            request = requests.post(self.apiroot, json={'query': query, 'variables': variables}, headers=self.headers)
            if request.status_code == 200:
                r =  request.json()
                # result_json= json.dumps(r, indent=2)
                
            else:
                raise Exception("Query failed to run by returning code of {}. {}".format(
                        request.status_code, query))
            
            return r
        
    def update_table (self, query, variables):
        """

        Args:
            query (String): You can write mutation graphql query to update 
            variables (stirng ): Values of each attributes needs to be updated

        Raises:
            Exception: _description_

        Returns:
            result_json (Json): Response for your request 
        """
        # use updateTablename() Mutation query 
        
        request = requests.post(self.apiroot, json={'query': query, 'variables': variables}, headers=self.headers)
        if request.status_code == 200:
            r =  request.json()
            result_json= json.dumps(r, indent=2)
            
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(
                    request.status_code, query))
        
        return result_json
    
    def delete_from_table (self, query, variables):
        """

        Args:
            query (String): You can write mutation graphql query to delete 
            variables (stirng ): Values of each attributes needs to be deleted

        Raises:
            Exception: _description_

        Returns:
            result_json (Json): Response for your request 
        """
        # use deleteTablename() Mutation query 
        
        request = requests.post(self.apiroot, json={'query': query, 'variables': variables}, headers=self.headers)
        if request.status_code == 200:
            r =  request.json()
            result_json= json.dumps(r, indent=2)
            
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(
                    request.status_code, query))
        
        return result_json
    
    
        
if __name__ == "__main__":
    obj = StrapiGraphql()
    
#     query = """mutation createUser($username:String!,$email:String!) { register(input: { username: $username, email: $email, password: $email } ) { user { id username email }  } }"""
# variables = {"username": "Nebiyu", "email":"neba.samuel17@gmail.com"}
    variables =  None
    # query = """ query getTraineeId{
    #                 trainees(pagination:{start:0,limit:200} filters:{batch:{Batch:{eq:5}}}){
    #                     data{
    #                     id
    #                     attributes{
    #                         trainee_id
    #                         email
                            
    #                     }
    #                     }
    #                 }
    #                 } """
    # print(obj.Select_from_table(query, variables=variables))
    # variables = {"email": "mahlet@10academy.org", "password":"12341234"}
    # print(obj.get_token())
    print(obj.headers)