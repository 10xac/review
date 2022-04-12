
import os, sys

from get_applicants import process_dataframe
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)

import mysql.connector as mysql
#import api
from secret import get_auth
from pandas.io import sql
import pandas as pd 
from sqlalchemy import create_engine
import json 
import collections
from datetime import datetime,date
import os
from get_applicants import split_dataframe

def get_dbauth():
    dbauth = get_auth(ssmkey='tenx/db/pjmatch',
                        envvar='RDS_CONFIG',
                        fconfig=f'{cpath}/.env/dbconfig.json')


    if 'username' not in dbauth.keys():
        if 'user' in dbauth.keys():
            dbauth['username'] = dbauth['user']
            
    
    return dbauth

def host_connect (dbName):
    dbauth = get_dbauth()
    try:
        conn = mysql.connect(
            host=dbauth['host'],
            user=dbauth['username'],
            password=dbauth['password'],
                            
        )
        
        cursor = conn.cursor()
        # print(f'creating database={dbName}')
        cursor.execute(f"CREATE DATABASE {dbName}")
        
        
    except Exception as e:
        print("Unable to create Database",e)

def db_connect(dbName="tenxdb" ):
    
    dbauth = get_dbauth()
    
    try:
        db = mysql.connect(
            host=dbauth['host'],
            user=dbauth['username'],
            password=dbauth['password'],
            database = dbName             
        )
    except Exception as e :
            print ("Unable to connet to Mysqlpass",e)  
   
    return db

def createTables(dbName):
    conn = db_connect(dbName)
    cur = conn.cursor()
    sqlFile = 'MYSQL_application_tables.sql'
    fd = open(sqlFile, 'r')
    readSqlFile = fd.read()
    fd.close()

    sqlCommands = readSqlFile.split(';')

    for command in sqlCommands:
        try:
            res = cur.execute(command)
        except Exception as ex:
            print("Command skipped: ", command)
            print(ex)
    conn.commit()
    cur.close()
    

def insert_data(dbname="tenxdb"):
    # try:
        db = db_connect()
        
        
        appliInfo = process_dataframe()
        appliInfo['time_stamp'] = appliInfo['time_stamp'].apply(lambda x: str(x))
        print(appliInfo.shape)
     
        for i, row in appliInfo.iterrows():  
              
            sqlQuery = ''' INSERT INTO applicant_information(time_stamp, email, firstname, english_level, commitment, self_funding,
                            graduated, pay_it_forward, renowned_idea, nationality, city, date_of_birth,
                            gender, education_level, field_of_study, name_of_instituition, honours,
                            github_profile, referee_name, previously_applied, mode_of_discovery,
                            work_experience, work_experience_details, python_proficiency, sql_proficiency, 
                            statistics_proficiency, algebra_proficiency, project_compeleted, data_science_profile, 
                            self_taught, Accept_terms_and_conditions, occupation, highest_completed_level_of_Education, graduation_date, linkedIn_profile, reason_to_join, 
                            previously_applied_batch, stage_to_pevious_application,
                            familyname, work_experience_month, batch)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s,
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                    %s, %s,%s,%s ,%s)
                '''
            
            cur =db.cursor(prepared=True) 
            data = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22],
                    row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], 
                    row[34], row[35],row[36], row[37], row[38], row[39], row[40])
            
            try:
                # Execute the SQL command
                
                cur.execute(sqlQuery,data)
                # Commit your changes in the database
                db.commit()
                print("All records are submitted successfully")
            except Exception as e:
                print("Error: ", e)
                # Rollback in case there is any error
                db.rollback()       
  
    
        
def db_execute_fetch(*args, many=False, tablename='', rdf=True, **kwargs):
    connection = db_connect(**kwargs)
    cursor1 = connection.cursor()
    
    if many:
        cursor1.executemany(*args)
    else:
        cursor1.execute(*args)
        
    # get column names
    field_names = [i[0] for i in cursor1.description]

    # get column values
    res = cursor1.fetchall()

    # get row count and show info
    nrow = cursor1.rowcount
    if tablename:
        print(f"{nrow} recrods fetched from {tablename} table")

    cursor1.close()
    connection.close()

    # return result
    if rdf:
        return pd.DataFrame(res, columns=field_names)
    else:
        return res


def retrive_reviewer(dbName):
    _ = db_connect(dbName)
    cur = _.cursor ()
    cur.execute(f"SELECT * from reviewer")
    res = cur.fetchall()
    return res

def getReviewers(reviewerGroup, dbName):
    _ = db_connect(dbName)
    cur = _.cursor ()
    cur.execute(f"SELECT * from reviewer where reviewer_group = {reviewerGroup}")
    res = cur.fetchall()

    return res

def fromTenx():
    query = "select * from applicant_information where batch =\"batch-5\"" 
    # where test_score >= 20"
    df = db_execute_fetch(query, rdf=True, dbName='tenxdb')
  
    return df

def update_appli_with_reviewer(dbName= 'tenxdb'):
    appliInfo = fromTenx()
    
    reviewersTwo = getReviewers(2, dbName)
    intervalTwo = len(appliInfo) // len(reviewersTwo)
    reviewTwoId = [reviewerTwo[0] for reviewerTwo in reviewersTwo]
    
    reviewersThree = getReviewers(3, dbName)
    
    intervalThree = len(appliInfo) // len(reviewersThree)
    reviewThreeId = [reviewerThree[0] for reviewerThree in reviewersThree]
    
    conn = db_connect(dbName)
    cur =conn.cursor(prepared=True)   
    for i, row in appliInfo.iterrows():
        
        applicant_id = row['applicant_id']
        
        if i <= intervalTwo:
            secondReviewerId = reviewTwoId[0]
        elif i > intervalTwo and i <= 2 * intervalTwo:
            secondReviewerId = reviewTwoId[1]
        elif i > 2 * intervalTwo and i <= 3 * intervalTwo:
            secondReviewerId = reviewTwoId[2]
        elif i > 3 * intervalTwo:
            secondReviewerId = reviewTwoId[3]

        if i <= intervalThree:
            thirdReviewerId = reviewThreeId[0]
        elif i > intervalThree and i <= 2 * intervalThree:
            thirdReviewerId = reviewThreeId[1]
        elif i > 2 * intervalThree:
            thirdReviewerId = reviewThreeId[2]
        
        # print(applicant_id, secondReviewerId)
        print(applicant_id, thirdReviewerId)
        
        sqlQuery= f""" UPDATE applicant_information SET 3rd_reviewer_id = {thirdReviewerId} WHERE applicant_id = {applicant_id}
                    """ 
        
        try:
            # Execute the SQL command
            
            cur.execute(sqlQuery)
            # Commit your changes in the database
            conn.commit()
            print("Updated Successfully")
        except Exception as e:
            print("Error: ", e)
            # Rollback in case there is any error
            conn.rollback()       
  

def showTables(q=None, **kwargs):
    if q is None:
        q = 'show tables'

    rdf = kwargs.pop('rdf', False)

    df = db_execute_fetch(q, rdf=False, **kwargs)

    print(df)

def alter_table( **kwargs):
    connection = db_connect(**kwargs)
    cursor1 = connection.cursor()
    # '2nd_reviewer_id', '2nd_reviewer_accepted', ALTER TABLE Customers
    #  NOT NULL; varchar(10) NOT NULL
    # 3rd_reviewer_accepted boolean 3rd_reviewer_id accepted  ALTER TABLE applicant_information ADD applicant_id INT AUTO_INCREMENT PRIMARY KEY
    try:
        query= "ALTER TABLE reviewer COLUMN reviwername VARCHAR(20) NOT NULL"
        cursor1.execute(query)
        print(f"Sucessfully altered")
    except Exception as e:
        print("Unable to alter",e)


 
def writeToReview(dbName):
    conn = db_connect(dbName)
    cur = conn.cursor()
    reviewers = [['evariste@10academy.org', 'evariste', 'Nizeyimana', 0],
                 ['yabebal@10academy.org', 'Yabebal', 'Tadesse', 1],
                 ['arun@10academy.org', 'Arun', 'Sharma', 2],
                 ['mahlet@10academy.org', 'Mahlet', 'Taye', 3]
                 ]

    for reviewer in reviewers:
        sqlQuery = """INSERT INTO reviewer(reviewer_email, firstname, lastname, reviewer_group) VALUES(%s, %s, %s, %s)
                   """
        data = (reviewer[0], reviewer[1], reviewer[2], reviewer[3])

        try:
            # Execute the SQL command
            cur.execute(sqlQuery, data)
            # Commit your changes in the database
            conn.commit()
            print("reviewers Inserted Successfully")
        except Exception as e:
            print("Error: ", e)
            # Rollback in case there is any error
            conn.rollback()
            
def update_tabele (**kwargs):
    
   
    try:
        connection = db_connect(**kwargs)
    
        cursor1 = connection.cursor()
          
        query ="""UPDATE reviewer
                SET reviewer_group = 2 where reviewer_id= 1 
                """
        cursor1.execute(query)

        connection.commit()
        
    

            
    except Exception as e:
        print("Unable to update",e)
            
   
if __name__ == "__main__":
    # print(showTables(dbName='tenxdb'))
   
    # host_connect(dbName='tenxdb')
    
    # createTables(dbName='tenxdb')
    
    # insert_data()
    
    
    # query = "describe applicant_information"
    
    # # batch ="batch-5"
    get_dbauth()
    # reviewerId = 4
    # query = f"SELECT * from applicant_information where 3rd_reviewer_id = {reviewerId}" 
    
    # # update_appli_with_reviewer()
    # df = db_execute_fetch(query, rdf=True, dbName='tenxdb')
    # print(df)
   