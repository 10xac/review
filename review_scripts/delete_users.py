import os,sys
curdir = os.path.dirname(os.path.realpath(__file__))
print(curdir)
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)
import  strapi_graphql

import pandas as pd



class DeleteUsers:
    def __init__(self, root = "dev-cms", ssmkey = "dev/strapi/token") -> None:
        self.root = root
        self.ssmkey = ssmkey
        self.sg= strapi_graphql.StrapiGraphql(root=self.root, ssmkey=self.ssmkey)
        
        
    def get_user(self):
        
        query =  """
                query getusers{
            usersPermissionsUsers(pagination:{start:0,limit:500}, filters:{role:{name:{eq:"Trainee"}}}){
                meta{
                pagination{
                    total
                }
                }
                data{
                id
                attributes{
                    email
                    
                }
                }
            }
            
            }
            """
        userJson = self.sg.Select_from_table(query=query, variables=None)
        user_df = pd.json_normalize(userJson['data']['usersPermissionsUsers']['data'])
        user_df= user_df.rename(columns={"attributes.email": "email"})
        
        return user_df
    def get_not_accepted_trainee(self):
 
        query= """ 
        
            query getTraineeId{
                            trainees(pagination:{start:0,limit:200} filters:{batch:{Batch:{eq:6}} Status:{eq:"Not_Accepted"}}){
                                data{
                                    id
                                    attributes{
                                        
                                        email
                                    all_user{
                                    data{
                                        id
                                        attributes{
                                        email
                                        
                                        }
                                    }
                                    }
                                    
                                }
                                }
                            }
                            }
                
                """
        traineeJson = self.sg.Select_from_table(query=query, variables=None)
        alluser_trainee = pd.json_normalize(traineeJson['data']['trainees']['data'])
        alluser_trainee= alluser_trainee.rename(columns={"id":"trainee_id",
            "attributes.email": "trainee_email",
                                                            "attributes.all_user.data.id": "all_user_id",
                                                            "attributes.all_user.data.attributes.email":"email"})
        # trainee_id = alluser_trainee[['all_user_id','email','trainee_email']]
        return alluser_trainee
    
    def email_mapper(self, emailString):
        mapper= {
            "u11252759@tuks.co.za":"abraham_pandu@yahoo.com",
            "koffivi.gbagbe@gmail.com":"koffivigbagbe@gmail.com",
            "gsinseswa721@daviscollege.com":"glorianiyonkurusinseswa@gmail.com",
            "djibriltcheugoue@yahoo.fr":"djibriltcheugoue@gmail.com"
                
            }
        return mapper.get(emailString, emailString)
    def process_user_data(self):
        not_accepted_df = self.get_not_accepted_trainee()
        not_accepted_df['email']= not_accepted_df['email'].map(lambda x: self.email_mapper(x))
        print(f"INFO: {not_accepted_df.shape} are not accepted for training ")
        
        user_df = self.get_user()
        merged_not_accepted = pd.merge(not_accepted_df, user_df, on="email", how ="left")
        print(f"INFO: {merged_not_accepted.shape} are not accepted for training with thier all user id")
        return merged_not_accepted
    
    def delete_user (self):
        dquery = """mutation deleteUser($userID:ID!){
                    deleteUsersPermissionsUser(id:$userID){
                        data{
                        attributes{
                            email
                            username
                        }
                        }
                    }
                    }"""
        not_accepted_df = self.process_user_data()
        null_id_df = not_accepted_df[not_accepted_df['id'].isnull()]
        print(f"WARNING: Number of trainee whose user id is null {null_id_df.shape} ")
        # for indx, row in not_accepted_df.iterrows():
        #     variables = {"userID": row['id']}
        #     # print(variables)
        #     r = self.sg.update_table (dquery, variables)
        #     print(r)
