import boto3
import psycopg2
import pandas as pd

def DBConnect():
    host = ""
    username = ""
    password = ""
    database = ""

    conn = psycopg2.connect(host=host, database=database, user=username, password=password)
    cur = conn.cursor()
    return conn, cur

def createTables():
    conn, cur = DBConnect()
    sqlFile = 'createPostgresTables.sql'
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

def intoPostgres():
    df = pd.read_csv('applicants_information')
    df.drop


createTables()
