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

def createDB():
    dbauth = get_secret()

    mydb = mysql.connect(host=dbauth['host'], user=dbauth['username'], password=dbauth['password'],
                         buffered=True)

    cur = mydb.cursor()
    cur.execute("CREATE DATABASE review")
    mydb.commit()
    cur.close()

def showDbs():
    dbauth = get_secret()
    mydb = mysql.connect(host=dbauth['host'], user=dbauth['username'], password=dbauth['password'],
                         buffered=True)

    cursor = mydb.cursor()
    cursor.execute("SHOW DATABASES")
    res = []
    for (databases) in cursor:
        res.append(databases[0].decode("utf-8"))

    df = pd.DataFrame(res, columns=['Database Names'])

    print(df)

createDB()
showDbs()
