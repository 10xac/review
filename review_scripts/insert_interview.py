import json
import os
import sys
import datetime
import numpy as np
import pandas as pd
curdir = os.path.dirname(os.path.realpath(__file__))
print(curdir)
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)


from review_scripts.strapi_graphql import StrapiGraphql
from review_scripts.strapi_methods import StrapiMethods
from question_mapper import column_mapper
from review_scripts.gdrive import gsheet


class InsertInterview:
    """ Class used to insert review that doesn't have prefilled response. 
        It will be used to insert Interview, One to one session etc.
    """ 
    def __init__(self, root="dev-cms", ssmkey="dev/strapi/token") -> None:
        
        self.root = root
        self.ssmkey = ssmkey
        self.sm = StrapiMethods(self.root, self.ssmkey)
        self.sg = StrapiGraphql(self.root, self.ssmkey)
    
    def get_accepted_trainee(self, sg, batch, Status):
        bquery = """
                query {
                    trainees(
                        pagination: { start: 0, limit: 100 }
                        filters: { batch: { Batch: { eq: 5 } }, Status: { eq: "Accepted" } }
                    ) {
                        meta {
                        pagination {
                            total
                        }
                        }
                        data {
                        attributes {
                            email
                            all_user {
                            data {
                                id
                                attributes {
                                email
                                }
                            }
                            }
                        }
                        }
                    }
                    }
            """
        traineeJson = self.sg.Select_from_table(
        query=bquery, variables={"batch": batch, "status": Status})

        traineedf = pd.json_normalize(traineeJson['data']['trainees']['data'])
        traineedf= traineedf.rename(columns={'attributes.all_user.data.id':'id'})
        return traineedf
    
    
    def get_reviewers(self,sg):
        query = """

        query getReviewer{
        reviewers(pagination:{start:0,limit:50} filters:{Email:{notIn:["nardos@10academy.org","yididya@10academy.org"]}}){
            data{
            id
            attributes{
            
                Email
            }
            }
        }
        
        }
        """
        reviewerJson = self.sg.Select_from_table(query=query, variables=None)

        reviewerdf = pd.json_normalize(reviewerJson['data']['reviewers']['data'])
        reviewers = reviewerdf['id'].to_list()
        return reviewers
    
    
    