import datetime
import boto3
import base64
import json
from google.protobuf import internal
import pandas as pd
import mysql.connector as mysql
from mysql.connector import Error
from botocore.exceptions import ClientError


def get_secret(secret_name="b4test-mysql", region_name="eu-west-1"):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print('failed')
        raise e

    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
    else:
        secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    return json.loads(secret)

def DBConnect(dbName=None):
    dbauth = get_secret()

    conn = mysql.connect(host=dbauth['host'], user=dbauth['username'], password=dbauth['password'],
                         database=dbName, buffered=True)

    cur = conn.cursor()
    return conn, cur

def createDB():
    conn, cur = DBConnect()
    cur.execute("CREATE DATABASE review")
    conn.commit()
    cur.close()

def showDbs():
    conn, cur = DBConnect()
    cur.execute("SHOW DATABASES")
    res = []
    for (databases) in cur:
        res.append(databases[0])

    df = pd.DataFrame(res, columns=['Database Names'])

    print(df)

def createTables(dbName):
    conn, cur = DBConnect(dbName)
    sqlFile = 'createMYSQLTables.sql'
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

def db_execute_fetch(*args, many=False, tablename='', rdf=True, **kwargs):
    connection, cursor1 = DBConnect(**kwargs)
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

def showTables(q=None, **kwargs):
    if q is None:
        q = 'SHOW TABLES'

    rdf = kwargs.pop('rdf', False)

    df = db_execute_fetch(q, rdf=True, **kwargs)

    print(df)

def fromTenx():
    query = "SELECT * from applicant_information"
    df = db_execute_fetch(query, rdf=True, dbName='tenxdb')

    return df

def fromTenxToReview():

    appliInfo = fromTenx()
    appliInfo.drop(["email", 'firstname', 'lastname', 'country', 'city', 'gender', 'name_of_instituition',
                    "previously_applied"], axis=1)

    appliInfo = appliInfo[['comfortability_speaking_english', 'commitment', 'self_funding', 'graduated',
                           'awareness_to_payback', 'renowned_idea', 'date_of_birth', 'education_level',
                           'field_of_study', 'honours', 'github_profile', 'referee_name', 'mode_of_discovery',
                           'work_experience', 'work_experience_details', 'python_proficiency', 'sql_proficiency',
                           'statistics_proficiency', 'algebra_proficiency', 'data_science_project',
                           'data_science_profile', 'self_taught', 'proceed_to_stage2']]

    interval = len(appliInfo) // 4

    conn, cur = DBConnect('review')
    for i, row in appliInfo.iterrows():
        sqlQuery = ''' INSERT INTO applicant_information(comfortability_speaking_english, commitment, self_funding,
                       graduated, awareness_to_payback, renowned_idea, date_of_birth, education_level,
                       field_of_study, honours, github_profile, referee_name, mode_of_discovery,
                       work_experience, work_experience_details, python_proficiency, sql_proficiency,
                       statistics_proficiency, algebra_proficiency, data_science_project, data_science_profile,
                       self_taught, proceed_to_stage2, reviewer_id)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''

        if i <= interval:
            data = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], 1)
        elif i > interval and i <= 2 * interval:
            data = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], 2)
        elif i > 2 * interval and i <= 3 * interval:
            data = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], 3)
        elif i > 3 * interval:
            data = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11],
                    row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], 4)

        try:
            # Execute the SQL command
            cur.execute(sqlQuery, data)
            # Commit your changes in the database
            conn.commit()
            print("applicants Inserted Successfully")
        except Exception as e:
            print("Error: ", e)
            # Rollback in case there is any error
            conn.rollback()

def writeToReview():
    conn, cur = DBConnect('review')
    reviewers = [['abubakar@10academy.org', 'Abubakar', 'Alaro'],
                 ['arun@10academy.org', 'Arun', 'Sharma'],
                 ['kevin@10academy.org', 'Kevin', 'Karobia'],
                 ['yabebal@10academy.org', 'Yabebal', 'Tadesse']]

    for reviewer in reviewers:
        sqlQuery = """INSERT INTO reviewer(reviewer_email, firstname, lastname) VALUES(%s, %s, %s)"""
        data = (reviewer[0], reviewer[1], reviewer[2])

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
