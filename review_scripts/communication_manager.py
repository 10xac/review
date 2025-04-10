class CommunicationManager:
    """All strapi queries are called from here"""
    def __init__(self):
        pass
    
    def create_user(self, sg, user_data):
        """
        Create a new user using the provided user data and return the result in JSON format.

        Parameters:
            sg: graphql object for interacting with the database
            user_data: a dictionary containing user's username and email

        Returns:
            result_json: the result of the user creation in JSON format
        """
        
        query = """mutation createUser($username:String!,$email:String!, $password:String!) 
                    { register(input: { username: $username, email: $email, password: $password } ) 
                    { user { id username email }  } }"""
        username = user_data['name']+"_"+ user_data['email']

        variables = {"username": username, "email":user_data['email'], "password":user_data['password']}

        result_json = sg.Select_from_table(query=query, variables= variables)
        return result_json
    
    def insert_all_users(self,sg, all_user_data):  
        query = """mutation createAllUser(
                $email: String
                $userId: ID
                $name: String
                $role: ENUM_ALLUSER_ROLE
                $batchId: [ID]
                $groups: [ID]
                ) {
                createAllUser(
                    data: {
                    email: $email
                    user: $userId
                    name: $name
                    role: $role
                    BatchIDs: $batchId
                    groups: $groups
                    }
                ) {
                    data {
                    id
                    }
                }
                }

                    """
        variables =  {"email": all_user_data['email'],"name":all_user_data['name'],
                        #"batch":all_user_data['batch'],
                        "userId": all_user_data['userId'], 
                        "role":all_user_data['role'],
                        "batchId": all_user_data['batchId'],
                        "groups": all_user_data['groups']
                        }
        result_json = sg.Select_from_table(query=query, variables= variables)
        return result_json
    def read_all_users(self,sg, req_params):
        query = """ query getAllUser($batch:Int,$role:String){
                allUsers(pagination:{start:0, limit:2000} filters:{Batch:{eq:$batch}, role:{eq:$role}}){
                    meta{
                    pagination{
                        total
                    }
                    }
                    data{
                    id
                    attributes{
                        name
                        email
                        Batch
                      	user{
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
        result_json = sg.Select_from_table(query=query, variables={"batch":req_params['batch'], "role": req_params['role']})
        return result_json
    
    def create_new_batch (self, sg,  batchparams ):
        """
        A function to create a new batch using the provided batch parameters and return the result JSON.
        
        Parameters:
            sg (object): An object used to interact with the database.
            batchparams (dict): A dictionary containing batch parameters such as batch number, class link, communication link, and additional information.
        
        Returns:
            dict: A JSON object containing the result of creating the new batch.
        """
        query = """mutation createBatch(
                $batch: Int
                $class_link: String
                $communication_link: String
                $additional_info: JSON
                ) {
                createBatch(data: {
                    Batch:$batch
                    Class_link:$class_link
                    Communication_link:$communication_link
                    additional_info:$additional_info
                    
                }) {
                    data {
                    id
                    }
                }
                }"""
        

        result_json = sg.Select_from_table(query=query, variables={"batch":batchparams['batch'], "class_link":batchparams['class_link'], 
                                                                   "communication_link":batchparams['communication_link'], 
                                                                   "additional_info":batchparams['additional_info']}) 
        return result_json
    

    def read_batch_information(self, sg, batch_params):
        bquery = """
            query getBatch($batch:Int){
            batches(filters: { Batch:  { eq: $batch } }){
                data{
                id
                attributes{
                    Batch
                    
                }
                }
            }
            }

            """
        # batch = int(self.batch.split("-")[1])
        batchJson = sg.Select_from_table(query=bquery, variables={"batch": batch_params['batch']})
        return batchJson
    
    def read_batch_from_batch_ID(self, sg, batch_id):
        query = """query getBatch($batch_ID:ID){
            batches(filters: { id:  { eq: $batch_ID } }){
                data{
                id
                attributes{
                    Batch
                    
                }
                }
            }
            }"""
        batchJson = sg.Select_from_table(query=query, variables={"batch_ID": batch_id})
     
        return batchJson
    def create_reviewer(self, sg, reviewer_data):
        query = """mutation createReviewer($allUserID:ID,$email:String,$batch:[ID]){
            createReviewer(data:{all_user:$allUserID,Email:$email,batches:$batch}){
                data{
                id
                attributes{
                    Email
                }
                }
            }
            }"""
        result_json = sg.Select_from_table(query=query,variables =  {"allUserID": reviewer_data['all_user'],
                                                                     "email": reviewer_data['Email'], 
                                                                     "batch": reviewer_data['batches']})
        return result_json
    def create_user_preference(self, sg, user_preference_data):
        query = """mutation createPreference(
                $mainUserID: ID
                $email: String
                $defaultSettings: JSON
                ) {
                createPreference(
                    data: {
                    defaultSettings: $defaultSettings
                    email: $email
                    users_permissions_user: $mainUserID
                    }
                ){
                    data{
                    id
                    }
                }
                }"""
        result_json = sg.Select_from_table(query=query, variables= {"mainUserID":user_preference_data['main_user_id'],
                                                                     "email": user_preference_data['email'],
                                                                     "defaultSettings":user_preference_data['defaultSettings']})
        return result_json
    def create_group_for_staff(self, sg, group_params):
        """Don't run as it is check for the default value """
        query = """mutation createGroupStaff($alluserIDS:[ID]){
            createGroup(data:{Name:"Staff",all_users:$alluserIDS}){
                data{
                id
                }
            }
            }"""
        groupJson = sg.Select_from_table(query=query, variables={"alluserIDS": group_params['alluserIDS']})
        return groupJson
    
    def read_batch_specific_reviewers(self, sg, batch):
        """
            Function to get current batch from strapi graphql

        Args:
            Self.batch (Int): Number that represent current batch 

        Returns:
            Strapi Id of the imputed batch 
        """
        bquery = """

            query getReviewer($batch: Int) {
                    reviewers(
                        pagination: { start: 0, limit: 100 }
                        filters: { batches: { Batch: { eq: $batch } } }
                    ) {
                        data {
                        id
                        attributes {
                            Email
                        }
                        }
                    }
                    }
            """
        batchJson = sg.Select_from_table(query=bquery, variables={"batch": batch})
        return batchJson
    
    # @@@@@ profile_data    {'first_name': 'Testapi', 
    #                        'last_name': 'First', 
    #                        'email': 'test@example.com', 
    #                        'nationality': 'Ethiopia',
    #                         'gender': 'Female', 
    #                         'date_of_birth': datetime.date(2025, 3, 31), 
    #                         'all_user': '2285', 'other_info': {'vulnerable': ''}, 
    #                         'bio': None, 
    #                         'city_of_residence': None}
    def insert_profile_information(self, sg, row):
        query = """mutation createProfileInformation(
            $firstName: String
            $surName: String
            $nationality: String
            $gender:String
            $email:String
  			$date_of_birth:Date
            $all_user:ID
  			$other_info:JSON
            $bio:String
            $city_of_residence:String
        ) {
            createProfileInformation(
            data: {
                first_name: $firstName
                surname: $surName
                nationality: $nationality
                gender:$gender
                all_user:$all_user
                email:$email
              	date_of_birth:$date_of_birth
              	other_info: $other_info
                bio:$bio
                city_of_residence:$city_of_residence
            }
            ) {
            data {
                id
            }
            }
        }"""
        print("profile row ......", row)    
     
      
        result_json = sg.Select_from_table(query=query, variables= { "firstName": row['first_name'],
                                                                        "surName": row['last_name'],
                                                                        "nationality": row["nationality"],
                                                                        "gender": row["gender"],
                                                                        "alluser": row["all_user"],
                                                                        "email": row["email"],
                                                                        "other_info": row["other_info"],
                                                                        "date_of_birth": row["date_of_birth"],
                                                                        "bio": row["bio"],
                                                                        "city_of_residence": row["city_of_residence"]
                                                                        })
        # print("result_json ......", result_json)
        return result_json
    
    def insert_trainee_information(self, sg,  row):
        query = """mutation createTrainees(
                    $email: String
                    $alluser: ID
                    $traineeID: String
                    $batch: ID
                    ) {
                    createTrainee(
                        data: {
                        email: $email
                        Status: Accepted
                        all_user: $alluser
                        trainee_id: $traineeID
                        batch:$batch
                        }
                    ) {
                        data {
                        id
                        }
                    }
                    }"""
        result_json = sg.Select_from_table(query=query, variables= row)
        return result_json
    
    def read_accepted_trainee(self,sg, trainee_params):
        bquery = """
                query get_trainee ($batch:Int, $status:String){
                    trainees(
                        pagination: { start: 0, limit: 1000 }
                        filters: { batch: { Batch: { eq: $batch } }, Status: { eq: $status } }
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
        traineeJson = sg.Select_from_table(
                                            query=bquery, 
                                            variables={"batch": trainee_params['batch'], 
                                                           "status": trainee_params['status']})
        return traineeJson

    def update_review_category_with_revewers(self, sg, reviview_category_params):
        query = """mutation updateReviewCategoryReviewers($id:ID!,$reviewers:[ID]){
            updateReviewCategory(id:$id,data:{reviewers:$reviewers}){
            data{
                attributes{
                name
                }
            }
            }
        }"""

        res = sg.Select_from_table(query = query, variables={'id': reviview_category_params['review_category_id'], 
                                                             'reviewers':reviview_category_params['reviewers']})
        return res
    def get_user_with_out_alluser( self, sg, role):
        query = """query getAllTrainees($role:String){
            usersPermissionsUsers(filters:{
                all_users:{id:{eq:null}}
                role:{name:{eq:$role}}}
            pagination:{start:0,limit:2000}){
                meta{
                pagination{
                    total
                }
                }
                data{
                id
                attributes{
                    email
                    username
                    all_users{
                    data{
                        attributes{
                        name
                        }
                    }
                    }
                }
                }
            }
            }"""
        result_json = sg.Select_from_table(query=query,variables =  {"role":role})
        return result_json
    
    def update_batch_user_for_group(self, sg, groupid : int, all_users_for_group):
        update_query = """mutation updateGroup($groupID:ID!,$allusersID:[ID]){
        updateGroup(id:$groupID,data:{all_users:$allusersID}){
            data{
            id
            }
        }
        }"""
        resu_json = sg.Select_from_table(query=update_query, variables={"groupID":groupid,"allusersID":all_users_for_group})
        print(resu_json)
        return resu_json
    
    def get_allUser_by_groupId(self, sg, groupId):
        query = """query getallUserID($groupID:ID){
        allUsers(
            pagination:{start:0,limit:2000}
            filters:{groups:{id:{eq:$groupID}}}){
            meta{
            pagination{
                total
            }
            }
            data{
            id
            }
        }
        }"""
        resu_json = sg.Select_from_table(query=query, variables={"groupID":groupId})
        with_group = [str(i['id']) for i in resu_json['data']['allUsers']['data']]
        return with_group
    
    def get_all_user_without_group (self, sg):
        query = """query getallUserID{
        allUsers(
            pagination:{start:0,limit:2000}
            filters:{groups:{id:{eq:null}}}){
            meta{
            pagination{
                total
            }
            }
            data{
            id
            }
        }
        }"""
        result_json = sg.Select_from_table(query=query, variables=None)
        without_group = [str(i['id']) for i in result_json['data']['allUsers']['data']]
        return without_group
    
    def get_user_with_out_alluser( self, sg, role):
        query = """query getAllTrainees($role:String){
                    usersPermissionsUsers(filters:{
                        all_users:{id:{eq:null}}
                        role:{name:{eq:$role}}}
                    pagination:{start:0,limit:2000}){
                        meta{
                        pagination{
                            total
                        }
                        }
                        data{
                        id
                        attributes{
                            email
                            username
                            all_users{
                            data{
                                attributes{
                                name
                                }
                            }
                            }
                        }
                        }
                    }
                    }"""
        result_json = sg.Select_from_table(query=query,variables =  {"role":role})
        return result_json

    def delete_user(self, sg, user_id: str):
        """Delete a user by ID"""
        query = """
        mutation deleteUser($id: ID!) {
            deleteUsersPermissionsUser(id: $id) {
                data {
                    id
                }
            }
        }
        """
        variables = {"id": user_id}
        return sg.Select_from_table(query, variables)

    def delete_alluser(self, sg, alluser_id: str):
        """Delete an alluser by ID"""
        query = """
        mutation deleteAllUser($id: ID!) {
            deleteAllUser(id: $id) {
                data {
                    id
                }
            }
        }
        """
        variables = {"id": alluser_id}
        return sg.Select_from_table(query, variables)

    def delete_profile(self, sg, profile_id: str):
        """Delete a profile by ID"""
        query = """
        mutation deleteProfile($id: ID!) {
            deleteProfile(id: $id) {
                data {
                    id
                }
            }
        }
        """
        variables = {"id": profile_id}
        return sg.Select_from_table(query, variables)

    def delete_trainee(self, sg, trainee_id: str):
        """Delete a trainee by ID"""
        query = """
        mutation deleteTrainee($id: ID!) {
            deleteTrainee(id: $id) {
                data {
                    id
                }
            }
        }
        """
        variables = {"id": trainee_id}
        return sg.Select_from_table(query, variables)
    
    
    def request_auth_query(self):
        auth_query = """
                    query {
                        me {
                        id
                username
                email
                role {
                name
                }
            }
            }
            """
        return auth_query

