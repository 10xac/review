import json
from urllib import response
import pandas as pd
import requests
import os, sys

from sqlalchemy import null
from gdive_util import gsheet
from process_application import ProcessApplication
from insert_response import InsertResponse
from secret import get_auth
curdir = os.path.dirname(os.path.realpath(__file__))
print(curdir)
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)
from strapi_methods import StrapiMethods as sm
from secret import get_auth

class FilterByQuiz:
    def __init__(self):
        self.api_url = "https://dev-cms.10academy.org"
        
        self.token = get_auth(ssmkey='dev/strapi/token',
                 envvar='STRAPI_TOKEN',
                 fconfig=f'{cpath}/.env/Strapi_token.json')
        
        print("Writing gspread config to /.env/Strapi_token.json")
        
   
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
    def select_from_applicant(self):
        dic_list= []
        
        table= f"https://dev-cms.10academy.org/api/applicant-informations?pagination[page]=0&pagination[pageSize]=1042"
        dic = sm.fetch_data(self, table,self.token['token'])
        df_0 = pd.json_normalize(dic['data'])
        
        pageCount = dic['meta']['pagination']['pageCount']
        dic_list.append(df_0)
        
       
        for i in range (pageCount):
            
            if i  == 0:
                continue
            else:
                
                table= f"https://dev-cms.10academy.org/api/applicant-informations?pagination[page]={i+1}&pagination[pageSize]=100"
                dic = sm.fetch_data(self, table,self.token['token'])
                df = pd.json_normalize(dic['data'])
                dic_list.append(df)
        return dic_list
    
    def get_applicant_gender(self):
        app_list =FilterByQuiz.select_from_applicant(self)
        merged = pd.concat(app_list)
        merged.rename(columns = {'attributes.email':'Email address'}, inplace = True)
        merged.rename(columns = {'attributes.gender':'gender'}, inplace = True)
        merged = merged [['Email address', 'gender']]
        new_df =  merged.drop_duplicates(subset=['Email address'], keep='first')
        return new_df
        
    def process_quiz (self):
        score_df = FilterByQuiz.get_quiz_result(self)
        transform = score_df.T
        transform.rename(columns = {"Email address: please ensure that you use the same email address as you used on your 10 Academy Batch 5 application.  Using a different email address will make it much more difficult for us to assign this result to you.":'Email address'}, inplace = True)
       
        user_list = ProcessApplication.select_from_trainees(self)
        
        merged = pd.concat(user_list)
        applicant_df = merged [merged['attributes.role']=="applicant"]
        
        applicant_df.rename(columns = {'attributes.email':'Email address'}, inplace = True)
        
        transform['Email address']= transform['Email address'].str.rstrip()
        transform['Email address']= transform['Email address'].str.lower()
        
        all_info_df = pd.merge(transform,applicant_df , on="Email address", how="left")
        all_info_df.rename(columns = {'attributes.name':'name'}, inplace = True)
       
        clean_df = all_info_df [['Score', 'Email address','id','name']]
        ids =  clean_df ['id'].to_list()
        # print(ids)
        
        gender_df = FilterByQuiz.get_applicant_gender(self)
        gender = gender_df.drop_duplicates(keep='first')
       
        with_gender = pd.merge(clean_df,gender , on="Email address", how="left")
        
        
     
       
        post_process = with_gender.dropna()
        # print("with gender",post_process)
        # return post_process
        return clean_df
    
        
    
    
    def flatten_json(y):
        out = {}

        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '_')
            elif type(x) is list:
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '_')
                    i += 1
            else:
                out[name[:-1]] = x

        flatten(y)
        return out
    
    def select_review_from_trainees(self,id):
        
        
        table= f"https://dev-cms.10academy.org/api/all-users/{id}?populate=%2A"
        dic = sm.fetch_data(self, table,self.token['token'])
       
        flat = FilterByQuiz.flatten_json(dic)
        df =  pd.json_normalize(flat)
        # print(df.columns)
        if 'data_attributes_reviews_data_1_id' in df.columns:
            review_id = df['data_attributes_reviews_data_1_id']
            email =  df['data_attributes_email']
        else:
            review_id = df['data_attributes_reviews_data_0_id']
            email =  df['data_attributes_email']
       
        return  review_id, email
       
  
    
    def score_val(self,row):
       
        split_string = row['Score'].split("/", 1)

        score = split_string[0]
        if row['gender']=="Female":
            
            
            return (int(score)+10)
        else:
            return score
       
    
    def get_review_data(self):
        quiz_data = FilterByQuiz.process_quiz(self)
        exclude_email = InsertResponse.process_with_question_type(self)
        valid_result = quiz_data[~quiz_data['Email address'].isin(exclude_email)]
        
        valid_result['newScore'] = valid_result.apply(lambda row: FilterByQuiz.score_val(self,row), axis=1)
        
        valid_result['newScore'] = valid_result['newScore'].astype('int32')
        filtered_score = valid_result[valid_result['newScore']>39]
        
        all_data = []
        
        table= "https://dev-cms.10academy.org/api/grades/"
        try:
           
            
            for index, row in filtered_score.iterrows():
               
                if int(row['id']) ==1082 or int(row['id']) ==1162 or int(row['id']) ==1196 or int(row['id']) ==620 or int(row['id']) ==481 or int(row['id']) ==772 or int(row['id']) ==1074 or int(row['id']) ==546 or int(row['id']) ==1299 or int(row['id']) ==1335 or int(row['id']) ==1303 or int(row['id']) ==1010 or int(row['id']) ==1371 or int(row['id']) ==829 or int(row['id']) ==531 or int(row['id']) ==1123 or int(row['id']) ==1034 or int(row['id']) ==1247 or int(row['id']) ==491 or int(row['id']) ==598 or int(row['id']) ==826 or int(row['id']) ==507 or int(row['id']) ==1067 or int(row['id']) ==694 or int(row['id']) ==1032 or int(row['id']) ==1311 or int(row['id']) ==1113 or int(row['id']) ==527 or int(row['id']) ==500 or int(row['id']) ==1252 or int(row['id']) ==1259 or int(row['id']) ==1137 or int(row['id']) ==1023 or int(row['id']) ==824 or int(row['id']) ==509 or int(row['id']) ==1155 or int(row['id']) ==1207 or int(row['id']) == 232 or int(row['id']) ==1178 or int(row['id']) ==892 or int(row['id']) ==1130 or int(row['id']) ==1238 or int(row['id']) ==533 or int(row['id']) ==800 or int(row['id']) ==360 or int(row['id']) ==847 or int(row['id']) ==739 or int(row['id']) ==259 or int(row['id']) ==719 or int(row['id']) ==746 or int(row['id']) ==521 or int(row['id']) ==847  or int(row['id']) ==1364 or int(row['id']) ==555 or int(row['id']) ==1211 or int(row['id']) ==817 or int(row['id']) ==1290 or int(row['id']) ==556 or int(row['id']) ==639 or int(row['id']) ==738 or int(row['id']) ==943 or int(row['id']) ==1286 or int(row['id']) ==886 or int(row['id']) ==553 or int(row['id']) ==1043:
                    continue
                else:
                    grade_id = int(row['id'])
                    
                    review_id, email= FilterByQuiz.select_review_from_trainees(self,int(row['id']))
                    
                    if row['newScore']<=39:
                        
                        grade_data ={
                            "label": "1hour_test",
                            "score": row['newScore'],
                            "all_user":int(grade_id),
                            "review":int(review_id)
                        }
                        print(grade_data)
                        
                        # sm.insert_data(self,grade_data,table, self.token['token']) 
                    else:
                        continue
                    # print(grade_data)
                    
        except Exception as e:
            print ("Unable to load",e)
        
            
        return valid_result
    
if __name__ == "__main__":
    obj = FilterByQuiz()
    # obj.process_quiz()
    # obj.get_review_data()
    # obj.select_review_from_trainees(id=847)
    obj.sanitycheck()
    
    