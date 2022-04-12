import os, sys
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)
    
from datetime import datetime, timedelta
import time
import requests
import json
#
import numpy as np
import pandas as pd
#
import mysql.connector as mysql
from mysql.connector import Error
import sqlalchemy as sqla

import boto3
import base64
from botocore.exceptions import ClientError
#
from utils import secret 

verbose = 1

class dbauth():
    def __init__(self, dbconfig={}, dbname='tenxdb'):
        self.dbname = dbname
        
        if dbconfig:
            self.dbconfig = dbconfig
        else:
            self.dbconfig = get_dbauth()
        
        #get MySQl engine
        self.engine = self.get_db_engine()
        
    def get_db_engine(self):
       
        dbname = self.dbname
        dbconfig = self.dbconfig
        
        engine_str = 'mysql+mysqldb://{user}:{password}@{host}/{dbname}'.format(dbname=dbname, **dbconfig)
        engine = sqla.create_engine(engine_str)
        
        return engine  


def get_dbauth(ssmkey='b4test-mysql', **kwargs):
    if verbose>0: 
        print(f'------GET_DBAUTH: using ssmkey={ssmkey}')
        
    auth = secret.get_auth(
                    ssmkey=ssmkey, 
                    envvar='RDS_CONFIG', 
                    fconfig=f'{cpath}/.env/{ssmkey}'
                    )
    
    if 'user' not in auth.keys():
        auth['user'] = auth['username']
        
    return auth



    
def get_connection(dbname,**kwargs):
    dbauth = get_dbauth(**kwargs)
    
    if verbose>0:
        print(f'GET_CONNECTION: using dbname={dbname}')
        
    mydb = mysql.connect(host=dbauth['host'] ,
      user=dbauth['user'],
      password=dbauth['password'],
      database=dbname)
    return mydb

def db_execute(*args,many=False,tablename='',multi=True,**kwargs):
    connection = get_connection(**kwargs)
    cursor1 = connection.cursor(buffered=True)
    if many:
        cursor1.executemany(*args)        
    else:
        cursor1.execute(*args, multi=multi)
    #
    nrow = cursor1.rowcount
    if tablename:
        print(f"{nrow} records inserted successfully into {tablename} table")        
    
    connection.commit()
    cursor1.close()
    connection.close()
    return nrow

def db_execute_fetch(*args, many=False, tablename='', rdf=True, **kwargs):
    connection = get_connection(**kwargs)
    cursor1 = connection.cursor()
    if many:
        cursor1.executemany(*args)        
    else:
        cursor1.execute(*args)
        
    
    #get column names
    field_names = [i[0] for i in cursor1.description]   
    
    #get column values
    res = cursor1.fetchall()

    #get row count and show info
    nrow = cursor1.rowcount
    if tablename:
        print(f"{nrow} recrods fetched from {tablename} table")        
    
    cursor1.close()
    connection.close()
    
    #return result
    if rdf:
        return pd.DataFrame(res, columns=field_names) 
    else:
        return res
            
def query_to_dict(ret):
    if ret is not None:
        return [{key: value for key, value in row.items()} for row in ret if row is not None]
    else:
        return [{}]
    
def show_dbs(**kwargs):
    dbauth = get_dbauth(**kwargs)
    mydb = mysql.connect(host=dbauth['host'] ,
      user=dbauth['user'],
      password=dbauth['password'],buffered=True)

    cursor = mydb.cursor()
    cursor.execute("SHOW DATABASES")
    res = []
    for (databases) in cursor:
         res.append(databases[0].decode("utf-8") )
            
    df = pd.DataFrame(res, columns=['Database Names'])
    
    return df
    
    
def show_tables(q=None, **kwargs):
    if q is None:
        q = 'SHOW TABLES'
        
    rdf = kwargs.pop('rdf',False)
        
    res = db_execute_fetch(q, rdf=False, **kwargs)
    res = [t[0].decode("utf-8") for t in res]
    df = pd.DataFrame(res,columns=['Table Names'])
    
        
    return df



#https://gist.github.com/janzell/dfe0041bdb5283ec8fc7f5db787ce348
def multiple_query(q, dbname=None, **kwargs):
    connection = get_connection(dbname=dbname, **kwargs)
    c = connection.cursor(buffered=True)
    # all SQL commands (split on ';')
    sqlCommands = q.split(';')

    for command in sqlCommands:
        if not command:
            continue 
            
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE commands
        try:
            res = c.execute(command)
            #print(f'{command[0:10]} .. is done!')      
        except Exception as ex:
            print("Command skipped: ", command)
            print(ex)

    connection.commit()
    c.close()   
    
def force_drop_table(table_name, dbname='tenxdb',q=None, **kwargs):
    q = f'''SET foreign_key_checks = 0;
    DROP TABLE {table_name};
    SET foreign_key_checks = 1;
    '''
    return multiple_query(q, dbname=dbname, **kwargs)
    
    #if q:
    #    db_execute(q, multi=False, dbname=dbname)        

def get_table_df(table_name, dbname='tenxdb',verbose=0, **kwargs):
    q = f'''
    SELECT *
    FROM {table_name}
    '''
    dfu = db_execute_fetch(q,dbname=dbname, **kwargs)
    if verbose>0:
        print(df.info())
        print(dff.head())    
        
    return dfu
  
def drop_then_add_table(table, q, dbname='tenxdb', **kwargs):
    force_drop_table(table, **kwargs)
    multiple_query(q,dbname=dbname, **kwargs)
    df = get_table_df(table)
    
    return df

def mysql_change_dtype(table=None, 
                       col=None, 
                       dtype=None, 
                       dbname='tenxdb', 
                       **kwargs):
    if table and col and dtype:
        table_name = table
        column_name = col
        data_type = dtype
    else:
        keys = 'table="table_name", col="column_name", dtype="data_type"'
        print(f'You must pass all of the following: {keys}')
        return None
        
    q = f'''
    ALTER TABLE {table_name}    
    MODIFY {column_name} {data_type};     
    '''
    res = db_execute(q,dbname=dbname, **kwargs)
    return res
     
def mysql_change_columns(table='trainees',
                          columns=['gclass_student_id', 'slack_student_id'],
                          target=['VARCHAR(30)', 'VARCHAR(30)'], 
                          dbname='tenxdb',
                          op='dtype',
                          verbose=1, **kwargs):
    
    if table and columns and target:
        table_name = table
        column_names = columns    
        target_list = target
        print(f'table_name={table_name}, column_names={column_names}, target={target_list}')
    else:
        keys = 'table="table_name", columns="[column_names]", target="[new_column_names if op==rename else dtypes]"'
        print(f'You must pass all of the following: {keys}')
        return None
    
    if verbose>0:
        print('------- before dtype change ------')
        print(get_table_df(table_name, **kwargs).info())
        print()
    
    q = f'''
    ALTER TABLE {table_name} 
    '''
    i=1
    
    #check expectation of input variables
    cond = isinstance(column_names,list) and isinstance(target_list,list)
    if not (cond and len(column_names)==len(target_list)):
        print('List length of column_names and target_list must be equal')
        return None
        
    for col, val in zip(column_names, target_list):
        if op == 'rename':
            command = f'RENAME COLUMN {col} TO {val}' 
        else: #dtype           
            command = f'MODIFY {col} {val}'
            
        if i<min([len(column_names), len(target_list)]):
            q += f'''         
            {command},        
            '''
        else:
            q += f'''         
            {command};        
            '''  
        i += 1
    
    if verbose>0:  
        print('Excuting the following SQL query: ')
        print(q)

    res = multiple_query(q, dbname=dbname, **kwargs)
    
    if verbose>0:
        print('------- after dtype change ------')
        print(get_table_df(table_name, **kwargs).info()) 
    
    return res

def mysql_addremove_columns(table=None,
                          columns=None,
                          dtype=None, 
                          dbname='tenxdb',
                          op='add',
                          verbose=1, **kwargs):
    
    if not op in ['add', 'drop', 'remove']:
        print("op must one of this: 'add', 'drop', 'remove' ")
        return None
    
    #if op is add, we must provide dtype
    cond = True
    if op =='add':        
        cond = dtype is not None
        
    if table and columns and cond:
        table_name = table
        column_names = columns
        if op =='add':
            print(f'table_name={table_name}, column_names={column_names}, dtype={dtype}')
        else:
            print(f'table_name={table_name}, column_names={column_names}')
    else:
        keys = 'table="table_name", columns="[column_names]", dtype="[dtypes if op==add]"'
        print(f'You must pass all of the following: {keys}')
        return None
    
    if verbose>0:
        print('------- before dtype change ------')
        print(get_table_df(table_name, **kwargs).info())
        print()
        
    #check that 
    if op =='add':
        cond = isinstance(column_names,list) and isinstance(dtype,list)
        if not (cond and len(column_names)==len(dtype)):
            print('List length of column_names and dtype must be equal')
            return None
    
    q = f'''
    ALTER TABLE {table_name} 
    '''
    
    for i, col in enumerate(column_names):
        if op == 'add':
            val = dtype[i]
            command = f'ADD {col} {val}' 
        elif op in ['drop', 'remove']:           
            command = f'DROP COLUMN {col}'
            
        if i+1<len(column_names):
            q += f'''         
            {command},        
            '''
        else:
            q += f'''         
            {command};        
            '''  
        i += 1
    
    if verbose>0:  
        print('Excuting the following SQL query: ')
        print(q)

    res = multiple_query(q, dbname=dbname, **kwargs)
    
    if verbose>0:
        print('------- after dtype change ------')
        print(get_table_df(table_name, **kwargs).info()) 
    
    return res
  

def create_db (dbname, **kwargs):
    q = f"CREATE DATABASE {dbname} IF NOT EXIST"
    return multiple_query(q, dbname=dbname, **kwargs)
        
    
def df_to_table(df, dbname="tenxdb", **kwargs):
    try:

        dbauth = get_dbauth(**kwargs)
        
        host=dbauth['host']
        password=dbauth['password']
        username=dbauth['username']            
        database  = dbname 
                                        
        engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/{dbname}')
        with engine.connect() as conn, conn.begin():
            
            df.to_sql('applicant_information', conn, if_exists='replace', index=False)
        db.commit()
        print("All records are submitted successfully")
        
    except Exception as e:
        print("unable to insert data", e)
        

def getReviewers(reviewerGroup, dbname, rdf=True, **kwargs):
    q = f"SELECT * from reviewer where reviewer_group = {reviewerGroup}"
    res = db_execute_fetch(q, rdf=rdf, dbname=dbname, **kwargs)

    return res

def fromTenx(dbname='tenxdb', **kwargs):
    query = "select * from applicant_information where batch =\"batch-5\"" 
    # where test_score >= 20"
    df = db_execute_fetch(query, rdf=True, dbname=dbname, **kwargs)
  
    return df

def update_appli_with_reviewer(dbname= 'tenxdb', **kwargs):
    appliInfo = fromTenx(**kwargs)
    reviewersTwo = getReviewers(2, dbname)
    intervalTwo = len(appliInfo) // len(reviewersTwo)
    reviewTwoId = [reviewerTwo[0] for reviewerTwo in reviewersTwo]
    
    reviewersThree = getReviewers(3, dbname, **kwargs)
    
    intervalThree = len(appliInfo) // len(reviewersThree)
    reviewThreeId = [reviewerThree[0] for reviewerThree in reviewersThree]
    
    conn = get_connection(dbname, **kwargs)
    cur =conn.cursor()   
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
    return 
  

def alter_table(**kwargs):
    connection = get_connection(**kwargs)
    cursor1 = connection.cursor()

    try:
        query= "ALTER TABLE reviewer COLUMN reviwername VARCHAR(20) NOT NULL"
        cursor1.execute(query)
        print(f"Sucessfully altered")
    except Exception as e:
        print("Unable to alter",e)


def create_tables_sqlfile(**kwargs):
        
    db = get_connection(**kwargs)
    cursor = db.cursor()
    sqlFile = 'createMYSQLTables.sql'
    fd = open(sqlFile, 'r')
    readSqlFile = fd.read()
    fd.close()

 
def writeToReview(dbname, **kwargs):
    conn = get_connection(dbname, **kwargs)
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
            
def update_table (**kwargs):
    
   
    try:
        connection = get_connection(**kwargs)
    
        cursor1 = connection.cursor()
          
        query ="""UPDATE reviewer
                SET reviewer_group = 2 where reviewer_id= 1 
                """
        cursor1.execute(query)

        connection.commit()
        
    

            
    except Exception as e:
        print("Unable to update",e)
            
   
if __name__ == "__main__":
    # print(showTables(dbname='tenxdb'))
   
    # host_connect(dbname='tenxdb')
    
    # createTables(dbname='tenxdb')
    # insert_data()
    # query = "describe application_information"
    
    query = "select * from applicant_information"
    # # update_appli_with_reviewer()
    df = db_execute_fetch(query, rdf=True, dbname='tenxdb')
    print(df['2nd_reviewer_id'].unique())
   