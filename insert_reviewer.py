import os, sys
curdir = os.path.dirname(os.path.realpath(__file__))
print(curdir)
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)


from secret import get_auth
from strapi_methods import StrapiMethods as sm
import pandas as pd


class InsertReviewer:
    def __init__(self):
        self.api_url = "https://dev-cms.10academy.org"
        
        self.token = get_auth(ssmkey='dev/strapi/token',
                 envvar='STRAPI_TOKEN',
                 fconfig=f'{cpath}/.env/Strapi_token.json')
        
        print("Writing gspread config to /.env/Strapi_token.json")
        
    def select_from_review(self):
        dic_list= []
        
        table= f"https://cms.10academy.org/api/reviews?pagination[page]=0&pagination[pageSize]=1042"
        dic = sm.fetch_data(self, table,self.token['token'])
        df_0 = pd.json_normalize(dic['data'])
        
        pageCount = dic['meta']['pagination']['pageCount']
        dic_list.append(df_0)
        
       
        for i in range (pageCount):
            
            if i  == 0:
                continue
            else:
                
                table= f"https://cms.10academy.org/api/reviews?pagination[page]={i+1}&pagination[pageSize]=100"
                dic = sm.fetch_data(self, table,self.token['token'])
                df = pd.json_normalize(dic['data'])
                dic_list.append(df)
        return dic_list
    
    def chunck_reviews(self):
        
        user_list = InsertReviewer.select_from_review(self)
        merged = pd.concat(user_list)
        total_reviewers = 9
        total_applicant= len (merged)
        reviwe_size = round(total_applicant/5)
        dfs = {}
        for n in range((merged.shape[0] // reviwe_size + 1)):
            df_temp = merged.iloc[n*reviwe_size:(n+1)*reviwe_size]
            df_temp = df_temp.reset_index(drop=True)
            dfs[n] = df_temp
            # if merged.shape[0] % reviwe_size != 0:
            #     df_temp = merged.iloc[-int(merged.shape[0] % reviwe_size):]
            #     df_temp = df_temp.reset_index(drop=True)
            #     dfs[n] = df_temp
            # else:
            #     pass
            
        return dfs

            
    def insert_reviwer (self):
        review_list = InsertReviewer.chunck_reviews(self)
        table = "https://cms.10academy.org/api/reviewers"
        for i in review_list:
            reviewId = review_list[i]['id'].to_list()
            
            if i == 0:
                reviewer_data1 = {
                    "Email":"mconton@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data2 = {
                    "Email":"mmusa@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data3 = {
                    "Email":"abdullahi@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data4 = {
                    "Email":"mahlet@10academy.org",
                    "reviews":reviewId,
                    "review_categories":1
                }
            elif i ==1:
                reviewer_data1 = {
                    "Email":"cswartz@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data2 = {
                    "Email":"mbaloyi@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data3 = {
                    "Email":"mesfin@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data4 = {
                    "Email":"evariste@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
            elif i ==2:
                reviewer_data1 = {
                    "Email":"won@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data2 = {
                    "Email":"donam@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data3 = {
                    "Email":"arun@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data4 = {
                    "Email":"bereket@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
            elif i ==3:
                reviewer_data1 = {
                    "Email":"akiiru@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                
                reviewer_data2 = {
                    "Email":"jbkwizera@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data3 = {
                    "Email":"yabebal@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data4 = {
                    "Email":"michael@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                
            elif i ==4:
                reviewer_data1 = {
                    "Email":"mmaina@10academy.org",
                     "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data2 = {
                    "Email":"mconton@10academy.org",
                    "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data3 = {
                    "Email":"arun@10academy.org",
                    "reviews":reviewId,
                    "review_categories":1
                }
                reviewer_data4 = {
                    "Email":"zelalem@10academy.org",
                    "reviews":reviewId,
                    "review_categories":1
                }
            else:
                break
            # print(reviewer_data1)
            # print(reviewer_data2)
            print(reviewer_data3)
            print(reviewer_data4)
            print("_________________________")
            # sm.insert_data(self,reviewer_data1,table, self.token['token']) 
            # sm.insert_data(self,reviewer_data2,table, self.token['token']) 
            # sm.insert_data(self,reviewer_data3,table, self.token['token']) 
            # sm.insert_data(self,reviewer_data4,table, self.token['token']) 
            


if __name__ == "__main__":
    obj = InsertReviewer()
    
    # table= "https://dev-cms.10academy.org/api/all-users"
    obj.insert_reviwer()