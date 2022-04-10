import boto3
import base64
import json
import gspread
# from df2gspread import df2gspread as d2g
import pandas as pd
import mysql.connector as mysql
from mysql.connector import Error
from botocore.exceptions import ClientError
from oauth2client.service_account import ServiceAccountCredentials as sac


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

def createDB(dbName):
    conn, cur = DBConnect()
    cur.execute(f"CREATE DATABASE {dbName}")
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

def fromReview():
    query = "SELECT * from applicant_information"
    df = db_execute_fetch(query, rdf=True, dbName='review')

    return df

def fromThoughtCoin():
    df = pd.read_csv('thoughtChain.csv')
    return df

def combinedfs():
    dfTenx = fromTenx()
    dfReview = fromReview()
    dfThot = fromThoughtCoin()

    removeCols = list(dfReview.columns)
    keepCols = ['renowned_idea', 'accepted', '2nd_reviewer_accepted', '3rd_reviewer_accepted']
    for col in keepCols:
        removeCols.remove(col)

    dfReview.drop(removeCols, axis=1, inplace=True)
    dfTenx.drop(['accepted'], axis=1, inplace=True)

    dfTenRev = pd.merge(dfTenx, dfReview, on='renowned_idea', how='left')

    rmCols = list(dfThot.columns)
    kpCols = ['First Name', 'Last Name', 'Thought Coins']
    for col in kpCols:
        rmCols.remove(col)

    dfThot.drop(rmCols, axis=1, inplace=True)
    dfThot.rename(columns={'First Name': 'firstname', 'Last Name': 'lastname'}, inplace=True)

    stripCols = ['firstname', 'lastname']
    for stripcol in stripCols:
        dfTenRev[stripcol] = dfTenRev[stripcol].apply(lambda x: str(x).lower().split())
        dfTenRev[stripcol] = dfThot[stripcol].apply(lambda x: str(x).lower().split())

    df = pd.merge(dfTenRev, dfThot, on=['firstname', 'lastname'], how='outer')
    df.to_csv("Week 0 final review.csv")

    return df

def writeToGsheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials_path = 'gsheet.json'

    credentials = sac.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(credentials)

    df = combinedfs()
    spreadsheetKey = "12LNLYLbkEhgVMs5yUMxQp_DmxY_k9s6Hy5rCVK_BEaA"
    sheetName = "sheet 1"
# d2g.upload(df, spreadsheetKey, sheetName, credentials, row_names=True)

combinedfs()
