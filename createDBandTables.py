import datetime
import boto3
import base64
import json
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

    res = db_execute_fetch(q, rdf=False, **kwargs)
    res = [t[0] for t in res]
    df = pd.DataFrame(res, columns=['Table Names'])

    print(df)

dbName = "review"
showTables(dbName=dbName)
