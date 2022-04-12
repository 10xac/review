import sys, os
import time
import glob
import json
import subprocess
import requests

import base64
import boto3
from botocore.exceptions import ClientError

region_name = "eu-west-1"

def write_aws_config():
    #check if /app exists
    home = os.environ.get('HOME','~')
    rdir = os.path.join(home, '.aws')
    fname = f'{rdir}/config'
    if not os.path.exists(fname):
        os.makedirs(rdir,exist_ok=True)
        print(f'writing aws config file to: {fname}')        
        with open(fname, 'a') as f:
            # f.write('[profile Jobmatch ] \n')
            # f.write('s3 = \n')
            # f.write('     signature_version = s3v4 \n')
            # f.write(f'region = {region_name} \n')       
            # f.write('output = json \n')

            f.write('[profile default] \n')
            #f.write('s3 = \n')
            #f.write('     signature_version = s3v4 \n')
            f.write(f'region = {region_name} \n')
            #f.write('output = json \n')            
           
    else:
        print(f'{fname} exists')

    
    return None

region_name = "eu-west-1"

def init_aws_session():
    # Create a Secrets Manager client
    # Create a Secrets Manager client
    session = boto3.session.Session(profile_name='default')
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    return client


def get_ssm_secret(secret_name):
    client = init_aws_session()

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])


    return secret

def config_from_string(sdata,fname=None):
    #check if /app exists     
    #if os.path.exists('/app'):
    #    rdir = '/app'

    data = json.loads(sdata)

    if fname:
        #make dir  
        if not os.path.dirname(fname):
            fname = f'~/.env/{fname}'        
        
        os.makedirs(os.path.dirname(fname),exist_ok=True)

    
        print(f'writing {fname} file ..')
        #dump it to json file       
        with open(fname, 'w') as outfile:
            json.dump(data, outfile)
        
    return data


def get_secret(pname, pvar=None,json=False,fname=''):
    
    authData = None
    if pvar is not None:
        if pvar in os.environ.keys():
            sdata = os.environ.get(pvar)
            authData = json.loads(sdata)
            return authData
    
    
    authData = config_from_string(get_ssm_secret(pname), fname=fname)
    #    
    return authData
    



def get_auth(ssmkey=None, envvar=None, fconfig=None):
  
    #pass through multiple alternatives to get credential
    if fconfig:            
        if os.path.exists(fconfig):
            try:
                print(f'reading auth from file: {fconfig} ..')        
                auth = json.load(open(fconfig))
                return auth
            except:
                print(f'reading {fconfig} failed!')

    if envvar:            
        if os.environ.get(envvar,''): 
            try:
                print(f'Getting {envvar} from environment ..')
                auth = config_from_string(os.environ.get(envvar,''),fname=fconfig)
                return auth
            except:
                print(f'getting enn variable {envvar} failed!')
                
    if ssmkey:
        try:
            print(f'Getting auth {ssmkey} from aws secret manager and saving it to {fconfig} ..')            
            auth = get_secret(ssmkey,fname=fconfig)
            return auth
        except Exception as e:
            print(f'getting secret {ssmkey} from aws ssm failed! ')
            #print(e)
            raise

    print('Crediential can not be obtained. Params are')
    print(f'ssmkey={ssmkey}, envvar={envvar}, fconfig={fconfig}')           
    raise

    return {}

#write .aws/config if it does not exist
_ = write_aws_config()

try:    
    #path = os.path.dirname(os.path.realpath(__file__))
    #path = os.path.dirname(path)
    path = os.environ.get('HOME','~')

    print('**Getting config files from ssm if they it is not already in .env folder ..')

    
    dbauth = get_auth(ssmkey='tenx/db/pjmatch',
                      envvar='RDS_CONFIG',
                      fconfig=f'{path}/.env/dbconfig.json')
    print(f'==tenx/db/pjmatch config saved: {path}/.env/dbconfig.json')
    
    # #
    # _ = get_auth(ssmkey="airtable-api-config",
    #              fconfig=f'{path}/.env/airtable_config.json',
    #              envvar='AIRTABLE_CONFIG',
    #              )
    # print(f'==airtable-api-config config saved: {path}/.env/airtable_config.json')

    #
    _ = get_auth(ssmkey="gspread/config",
                 fconfig=f'{path}/.env/gclass_credentials.json',
                 envvar='GSPREAD_CONFIG',
                 )
    print(f'==gspread/config config saved: f{path}/.env/gclass_credentials.json!')
    
except Exception as e:
    print('ERROR: Unable to fetch ssm params!')
    print(e)
    



