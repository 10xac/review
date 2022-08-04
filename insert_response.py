
from enum import unique
import json
import sys, os
from types import new_class
import pandas as pd
from numpy import mat
from gdive_util import gsheet
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

class InsertResponse:
    
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
        
        df = InsertResponse.prepare_applicants(self)
        result = df.to_json(orient="records", date_format = 'iso')
       
        for data in json.loads(result):
            sm.insert_data(self,data,table, token = self.token['token'])
        
        print("All records are inserted") 
        
        
    def select_from_trainees(self):
        dic_list= []
        
        table= f"https://dev-cms.10academy.org/api/all-users?pagination[page]=0&pagination[pageSize]=1042"
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
    def get_quiz_result(self):
        sid_radar = '1_DRJTusGRG-S_V3xaTjTVSj6Ou2KVI3jGKxOe7D5dHc'
        gd = gsheet(sheetid=sid_radar,fauth='gdrive_10acad_auth.json')   
        sname = f'Form responses 1'
        
        try:
            df = gd.get_sheet_df(sname)
            
            # print(df.head())
            # print(f'------------{sname} df.shape={df.shape}----')
            
        except Exception as e:
            print(f'ERROR: Could not obtain sheet for {sname}',e)
            
        
        return df
    
    def process_quiz (self):
        score_df = InsertResponse.get_quiz_result(self)
        transform = score_df.T
        transform.rename(columns = {"Email address: please ensure that you use the same email address as you used on your 10 Academy Batch 5 application.  Using a different email address will make it much more difficult for us to assign this result to you.":'Email address'}, inplace = True)
       
        user_list = InsertResponse.select_from_trainees(self)
        merged = pd.concat(user_list)
        applicant_df = merged [merged['attributes.role']=="applicant"]
        
        applicant_df.rename(columns = {'attributes.email':'Email address'}, inplace = True)
       
        transform['Email address']= transform['Email address'].str.rstrip()
        transform['Email address']= transform['Email address'].str.lower()
        
        all_info_df = pd.merge(transform,applicant_df , on="Email address", how="left")
        clean_df = all_info_df [['Score', 'Email address','id']]
       
        post_process = clean_df.dropna()
        return post_process
    
    
    def process_with_question_type(self):
        graduation =  "When is your graduation date? Put your expected graduation date if you are still studying (Note: Applicants whose graduation date is between 1 Jan 2020 and 30 April 2022 are likely to be prioritized - a proof will be asked for at a later stage of the process)"
        user_list = InsertResponse.select_from_trainees(self)
        
        merged = pd.concat(user_list)# from strapi
        # print("strapi",merged.shape)
        app_df = get_applicant_data() # from Gsheet
        df = app_df.T 
        df['Timestamp'] = df['Timestamp'].apply(lambda x: datetime.datetime.strptime(x, "%d/%m/%Y %H:%M:%S"))
        df['Year'] = df['Timestamp'].dt.year
        reason = 'I agree that 10 Academy can use my application information for processing my application and for keeping me informed of further opportunities in related fields. We will not share/sell your information. Our full terms and conditions are here: https://docs.google.com/document/d/1yduZ66dH5o8vA_scA3N6tOla9OeJuhoFRGTQ35KsG0g/edit?usp=sharing and our privacy policy is here: https://docs.google.com/document/d/1jhZqUb2S92UM5wjMzPlRpHew_A5xjkRgLK7gZfpoAik/edit?usp=sharing'
        new_idea="Imagine you were asked to design and implement a project. The project will use technology (AI, Web3, others) to positively impact at least 5 million people in 5 years in a sustainable (financially, environmentally) and scalable way. Briefly describe the problem you would choose (from any field e.g agriculture, education, etc) and how your solution will be impactful, scalable, and sustainable. Detailed answers are helpful. (1500 characters max)"
        pay_it_forward= "Please confirm that you have read and are in agreement with the costs and pay-it-forward model for 10 Academy Batch 5 "
        obligation = "If you are admitted to 10 Academy's Batch 5 intensive training, are you able to commit full-time (~60 hours/week) without conflicting obligations?"
        self_fund  ='Are you able to self-fund and provide the technical requirements for our remote training?'
        df[graduation] = pd.to_datetime(df[graduation], errors='coerce')
        df['Date of Birth']= pd.to_datetime(df["Date of Birth"], errors = 'coerce')
        quiz_data = InsertResponse.process_quiz(self)
        valid_email = quiz_data['Email address'].to_list()
        
        # filtered_df = df[(df[reason].str.len() >= 100)]
        filtered_df = df[(df[new_idea].str.len() >= 100) ]
        filtered_df = filtered_df[(filtered_df[pay_it_forward].str.lower()=='yes')]
        filtered_df = filtered_df[(filtered_df[reason].str.lower()=='yes')]
        filtered_df = filtered_df[(filtered_df[obligation].str.lower()=='yes')]
        filtered_df = filtered_df[(filtered_df[self_fund].str.lower()=='yes')]
        # filtered_df = filtered_df[(filtered_df['Date of Birth']>='1/1/1992')]
        
       
        
       
        applicant_df = merged [merged['attributes.role']=="applicant"]
        print("applicant",applicant_df.shape)
        
        useremail = merged['attributes.email'].to_list()
        applicant_df['attributes.email'].to_csv("strapi_email.csv")
        new_df =  filtered_df.drop_duplicates(subset=['Email address','First Name(s)/Given Name(s)'], keep='first')
        applicant_df.rename(columns = {'attributes.email':'Email address'}, inplace = True)
       
        print ("clean",new_df.shape)
        
        # all_info_df= pd.concat([new_df,applicant_df ], axis=0, ignore_index=True)
        all_info_df = pd.merge(new_df,applicant_df , on="Email address", how="left")
       
        cos_drop= ['attributes.name', 'attributes.role',
       'attributes.createdAt', 'attributes.updatedAt',
        'attributes.image_link']
        value = all_info_df.drop(cos_drop, axis = 1)
        
        value['Timestamp'] = value['Timestamp'].astype(str)
        value.fillna("null")
        new = value[value['Year']==2022]
        print("test result",len(valid_email))
        valid_response = new[new['Email address'].isin(valid_email)]
        not_valid_response = new[~new['Email address'].isin (valid_email)]
        exclude_emails= not_valid_response['Email address'].to_list()
        print(len(exclude_emails))
        
        

       
     
        text_filed = ['Email address','First Name(s)/Given Name(s)','Family Name(s)/Surname(s)',
                      'City of current residence','Field of Study','Name of Institution','Special academic achievements and honors',
                      'GitHub Profile Link','LinkedIn Profile Link', 'Name of Reference',
                      'Work Experience Specifications','How many months of full-time work experience do you have as of 31 Mar 2022?',
                      'Kaggle/Zindi Profile Link',]
        
        check_box = ['Work Experience so far if any','How did you learn about 10 Academy and this program?']
        date = ['Timestamp','Date of Birth','When is your graduation date? Put your expected graduation date if you are still studying (Note: Applicants whose graduation date is between 1 Jan 2020 and 30 April 2022 are likely to be prioritized - a proof will be asked for at a later stage of the process)']
        long_text = ['Imagine you were asked to design and implement a project. The project will use technology (AI, Web3, others) to positively impact at least 5 million people in 5 years in a sustainable (financially, environmentally) and scalable way. Briefly describe the problem you would choose (from any field e.g agriculture, education, etc) and how your solution will be impactful, scalable, and sustainable. Detailed answers are helpful. (1500 characters max)',
                     'Why do you want to join 10 Academy Batch 5 Intensive Training? Help our team to understand your past work, your future goals and how your taking up 10 Academy training will help you (and those around you) to grow. (1500 characters max)',
                     'Please describe, in detail, any self-taught or extra-curricular data science-related courses that you have undertaken or completed.']
        length_cols= value.columns
        table = "https://dev-cms.10academy.org/api/reviews/"
        # table = "https://cms.10academy.org/api/reviews/"
        response=[]
        for index, row in valid_response.iterrows():
            prefilled_res=[]
            for i in length_cols:
                if i =='id':
                    continue
                elif i in  text_filed:
                    dic = {
                        "type": "textbox",
                        "label": i,
                        "answer": str(row[i]),
                        "required": "true"
                                
                            }
                elif i in long_text:
                    dic = {
                        "type": "textarea",
                        "label": i,
                        "answer": str(row[i]),
                       
                        "required": "true"
                                
                            }
                elif i in date:
                    dic = {
                        "type": "date",
                        "label": i,
                        "answer": str(row[i]),
                        
                        "required": "true"
                                
                            }
                elif i in check_box:
                    dic = {
                        "type": "multi-select",
                        "label": i,
                        "answer": str(row[i]),
                       
                        "required": "true"
                                
                            }
                else:
                    dic = {
                        "type": "radio",
                        "label": i,
                        "answer": str(row[i]),
                      
                        "required": "true"
                                
                            }
                    
                prefilled_res.append(dic)
            to_send= {
                "status": "Not_reviewed",
                "prefilled_response":prefilled_res,
                "all_user":row['id'],
                "review_category":1
            }
            
        
            sm.insert_data(self,to_send,table, self.token['token'])   
           
        return exclude_emails
        
        
        
if __name__ == "__main__":
    obj = InsertResponse()
    
    # table= "https://dev-cms.10academy.org/api/all-users"
    obj.process_with_question_type()