import json
import os
import sys
import datetime
import numpy as np
import pandas as pd
from review_scripts.communication_manager import CommunicationManager


from review_scripts.strapi_graphql import StrapiGraphql
from review_scripts.strapi_methods import StrapiMethods
from utils.question_mapper import column_mapper
from utils.gdrive import gsheet


class InsertInterview:
    """ Class used to insert review that doesn't have prefilled response. 
        It will be used to insert Interview, One to one session etc.
    """ 
    def __init__(self, run_stage = "dev-cms", **kwargs) -> None:
        
        self.sm = StrapiMethods(run_stage= run_stage)
        self.sg = StrapiGraphql(run_stage= run_stage)
        self.cm = CommunicationManager()
        self.batch =  kwargs.get("batch", 8)
        self.status = kwargs.get("status", "Accepted")
        self.sid_interview_admited = kwargs.get("sid_interview_admited", "1Z6hRjM7qPnqg7g5F6Q5R9Jz5jDp9h9jXx5V0CwEYq5Q")
        self.sheet_name = kwargs.get("sheet_name", "Admitted Trainees")
        self.review_category_id =  kwargs.get("review_category_id", "16")

    def get_interview_admitted_trainees(self):
        """
        Function to read application from google sheet. 
        Args: 
            sid_application: sheet id for the application information 
        Returns:
            df: dataframe
        """

        if self.sid_interview_admited:
            gd = gsheet(sheetid=self.sid_interview_admited,
                        fauth='admin-10ac-service.json')
        else:

            gd = gsheet(sheetid="1mG8uNDxaDfNq-iRi-_-mgsz5rArkrMPAXtV8IR53xXM",
                    fauth='admin-10ac-service.json')
   

        try:
            df = gd.get_sheet_df(self.sheet_name)

            # print(df.head())
            print(f'------------{self.sheet_name} df.shape={df.shape}----')

        except Exception as e:
            print(f'ERROR: Could not obtain sheet for {self.sheet_name}', e)

        return df
    def get_accepted_trainee(self):
        params  =  {
            "batch": self.batch,
            "status": self.status
        }
        trainee_json = self.cm.read_accepted_trainee(self.sg, params )

        traineedf = pd.json_normalize(trainee_json['data']['trainees']['data'])
        traineedf= traineedf.rename(columns={'attributes.all_user.data.id':'id'})
        return traineedf
  
    
 
    def get_reviewers(self):
        review_json = self.cm.read_batch_specific_reviewers(self.sg, self.batch)

        reviewerdf = pd.json_normalize(review_json['data']['reviewers']['data'])
    
        reviewers = reviewerdf['id'].to_list()
        return reviewers
            
 
    def insert_review(self,  df, reviewers):
        table = "reviews"
        for i, row in df.iterrows():

            tosend =  {
                    "status":"Ongoing",
                    "all_user":row['id'],
                    "review_category":self.review_category_id,
                    
                    "reviewers": reviewers

            }
            review_result = self.sm.insert_data(tosend,table)
            print(review_result)
    
    def insert_interview(self):
        ##get_accepted traienees 
        
        df = self.get_interview_admitted_trainees()
        ### get trainee data 
        traineedf = self.get_accepted_trainee()
        traineedf.rename(columns={"attributes.email":"trainee_email", 
                            "attributes.all_user.data.attributes.email":"email"}, inplace=True)
        df.rename(columns= {'Email':'email'}, inplace=True)
        merged_df = pd.merge( df,traineedf, on="email", how= "left")
        df_final = merged_df[~merged_df['id'].isna()]
        ### update review category
        reviewers = self.get_reviewers()
        params = {
            'review_category_id': self.review_category_id, 
            'reviewers':reviewers
        }
        self.cm.update_review_category_with_revewers(self.sg, params)
        self.insert_review(df_final, reviewers)
        return df_final
    
    