import sys, os
import time
import glob
import json
import subprocess
import requests
import tempfile
import base64
import boto3
from botocore.exceptions import ClientError

region_name = "us-east-1"

def init_aws_session():
    # Create a Secrets Manager client
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    return client


def create_secret(secret_name, key, value):
    client = init_aws_session()

    # get original secrets
    res = client.update_secret(SecretId=secret_name, SecretString=json.dumps({key: value}))

    return res

def update_secret(secret_name, kv):
    client = init_aws_session()
    # get original secrets
    secret = get_secret(secret_name)
    secret.update(kv)
    res = client.update_secret(SecretId=secret_name, SecretString=json.dumps(secret))
    #print(secret)
    return res


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
        elif 'SecretBinary' in get_secret_value_response.keys():
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        else:
            secret = get_secret_value_response


    return secret


def config_from_string(sdata,fname=None,rfile=False):
    '''
    sdata: string data
    fname: file name to save
    rfile: return file object
    '''

    if isinstance(sdata, str):
        data = json.loads(sdata)
    else:
        data = sdata

    try:
        if fname:
            #make dir  
            if not os.path.dirname(fname):
                fname = lambda_friendly_path(fname)
        
            os.makedirs(os.path.dirname(fname),exist_ok=True)

            print(f'writing {fname} file ..')
            #dump it to json file       
            with open(fname, 'w') as f:
                json.dump(data, f)

            if rfile:
                return fname
            else:
                return data
    except:
        print(f'------warning: saving {fname} failed----')
        return None
        


def get_secret(pname, pvar=None,fname=''):
    
    authData = None
    if pvar is not None:
        if pvar in os.environ.keys():
            sdata = os.environ.get(pvar)
            authData = json.loads(sdata)
            return authData
    
    
    authData = config_from_string(get_ssm_secret(pname), fname=fname)
    #    
    return authData
    
def get_secret_env(pname, pvar=None,fname=''):
    
    authData = None
    if pvar is not None:
        if pvar in os.environ.keys():
            sdata = os.environ.get(pvar)
            authData = json.loads(sdata)
            return authData
    
    
    authData = json.loads(get_ssm_secret(pname))
    #    
    return authData    

def is_lambda():
    c1 = os.environ.get("LAMBDA_TASK_ROOT") is not None
    c2 = os.environ.get("AWS_EXECUTION_ENV") is not None
    c3 = os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None

    return c1 or c2 or c3

def lambda_friendly_path(fpath):
    basename = os.path.basename(fpath)
    dirname = tempfile.gettempdir()
    if is_lambda():
        f = f'/tmp/{basename}'
    else:
        os.makedirs(dirname, exist_ok=True)
        f = f"{dirname}/{basename}"
    return f


def get_auth(ssmkey=None, envvar=None, fconfig=None, rfile=False):
    '''
    Wrapper to get auth from ssm, env or file

    ssmkey: secret manager key
    envvar: environment variable name
    fconfig: file name
    rfile: return file object

    '''
    caller_line_number = sys._getframe(1).f_lineno        
    caller_filename = sys._getframe(1).f_code.co_filename
    caller_filename = caller_filename.split('/')[-1] if '/' in caller_filename else caller_filename      
    caller_func_name = sys._getframe(1).f_code.co_name    
    print(f'{caller_filename}:{caller_func_name}:{caller_line_number}: get_auth(ssmkey={ssmkey}, envvar={envvar}, fconfig={fconfig})')

    if not fconfig:
        fconfig = '.env/auth_{ssmkey}.json'

    #if in lambda write only in /tmp folder    
    fconfig = lambda_friendly_path(fconfig)
        
    #pass through multiple alternatives to get credential
    if fconfig:                    
        if os.path.exists(fconfig):
            try:
                print(f'reading auth from file: {fconfig} ..')        
                with open(fconfig) as json_file:
                    auth = json.load(json_file)
                return auth
            except:
                print(f'reading {fconfig} failed!')

    if envvar:            
        if os.environ.get(envvar,'') not in ['','null','None']: 
            try:
                print(f'Getting {envvar} from environment ..')
                auth = config_from_string(os.environ.get(envvar,''),fname=fconfig, rfile=rfile)
                #print('auth from env is:',auth)
                return auth
            except:
                print(f'getting env variable {envvar} failed!')
                
    if ssmkey:
        
        try: 

            keys = {
                    'strapi/alml-cms/token':'ALML_STRAPI_TOKEN',
                    'staging/strapi/token':'TENX_STAGING_STRAPI_TOKEN',
                    'dev/strapi/token':'TENX_DEV_STRAPI_TOKEN',
                    'prod/strapi/token':'TENX_PROD_STRAPI_TOKEN',
                    'git_token_tenx':'GIT_TOKEN_10ACADEMY',
                    'tenx/db/strapi': {
                                        'STRAPI_PGDB_USERNAME':'username',
                                        'STRAPI_PGDB_PASSWORD':'password',
                                        'STRAPI_PGDB_ENGINE':'engine',
                                        'STRAPI_PGDB_HOST':'host',
                                        'STRAPI_PGDB_PORT':'port',
                                        'STRAPI_PGDB_IDENTIFIER':'dbInstanceIdentifier'
                    },
                    'strapi/prod/email':[
                                            'AWS_SES_KEY',
                                            'AWS_SES_SECRET'
                    ]
                   }

            # by default try to get all requested from tenx/env/vars
            sname = 'tenx/env/vars'
            rname = lambda_friendly_path('.env/tenx_env_vars.json')
                                         
            if not os.path.exists(rname):
                print(f'Getting {sname} from aws secret manager ..')
                authTemp = get_secret_env(sname)
                _ = config_from_string(authTemp,fname=rname,rfile=True)
            else:
                print(f'Getting {sname} from existing file {rname}..')
                with open(rname) as json_file:
                    authTemp = json.load(json_file)


            if ssmkey in keys.keys() or ssmkey in authTemp.keys():
                if ssmkey in authTemp.keys():
                    auth = authTemp[ssmkey]
                else:
                    res = keys[ssmkey]

                    if type(res) is dict:
                        #res is dict
                        auth = {}
                        for kold,knew in res.items():
                            auth[knew] = authTemp[kold]
                    elif type(res) is list:
                        #res is list
                        auth = {}
                        for k in res:
                            auth[k] = authTemp[k]
                    else:
                        #res is string
                        auth = authTemp[res]
            else:
                print(f'Getting {ssmkey} from aws secret manager as it can not be found in {sname} ..')
                auth = get_secret(ssmkey,fname=fconfig)   

            if rfile:
                if os.path.exists(fconfig):
                    print(f'Returning {fconfig} from existing file ..')
                    return fconfig
                else:
                    print(f'Returning {fconfig} by writing to file ..')
                    return config_from_string(auth,fname=fconfig,rfile=rfile)   
            else:             
                return auth
            
        except Exception as e:
            print(f'getting secret {ssmkey} from aws ssm failed! ')
            #print(e)
            raise

    print('Crediential can not be obtained. Params are')
    print(f'ssmkey={ssmkey}, envvar={envvar}, fconfig={fconfig}')           
    raise

    return {}

def get_google_service_account(ssmkey="gspread/config",
                                envvar="gclass_credentials.json",
                                fconfig=".env/gclass_credentials.json",
                                rfile=True):
    
    caller_line_number = sys._getframe(1).f_lineno        
    caller_filename = sys._getframe(1).f_code.co_filename
    caller_filename = caller_filename.split('/')[-1] if '/' in caller_filename else caller_filename      
    caller_func_name = sys._getframe(1).f_code.co_name    
    print(f'{caller_filename}:{caller_func_name}:{caller_line_number} Getting google service account ..')

    return get_auth(ssmkey=ssmkey,
                    envvar=envvar,
                    fconfig=fconfig, 
                    rfile=rfile)                    
  
    

if __name__ == "__main__":
    
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.dirname(path)

    # dbauth = get_auth(ssmkey='tenx/db/pjmatch',
    #                   envvar='RDS_CONFIG',
    #                   fconfig=f'{path}/.env/dbconfig.json')
    # print('**Getting config files from ssm if they it is not already in .env folder ..')
    # print('=====================================')
    print(path)
    _ = get_auth(ssmkey="tenx/env/vars",
                 fconfig=f'{path}/.env/tenx_env_vars.json',
                 envvar='all_tenx_env_vars',
                 )
    print(_)
