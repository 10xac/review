import os, sys
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)
#
import json
import pandas as pd
#
from airtable import Airtable
import utils.secret as usc
 

def get_api_key(fname=None):
    fname = '/Users/yabebal/.credentials/airtable_api_key.json'
    api_key = json.load(open(fname, 'r'))['API_KEY']
    return api_key


def get_table(name_list, 
              fconfig='.env/airtable_config.json',
              ssmkey="airtable-api-config",
              envvar='AIRTABLE_API_CONFIG',
              fields=None, 
              verbose=0):
    '''
        Get tables from Airtable.  are passed in the

        Params:
            - name_list: the list of table names
            - fields: a dictionary with keys table names and values list of column names
            - secret_json: the Airtable config file in json
    '''
    
    #get api key and secret
    secret = usc.get_auth(ssmkey=ssmkey, envvar=envvar, fconfig=fconfig)
        
    if secret:
        try:
            base_key = secret['base_key']
            api_key = secret['api_key']
        except:
            base_key = secret['BASE_KEY']
            api_key = secret['API_KEY']

    else:
        print(f'{secret_json} does not exist!')
        print('Airtable Base_KEY and API_KEY should be passed\
             in a json file using secret_json key')
        return pd.DataFrame()

    df_list = {}
    for table_name in name_list:

        airtable = Airtable(base_key, api_key)
        records = airtable.iterate(table_name,
                                   fields=fields.get(table_name, None))

        if verbose > 0:
            print(f'----------table_name={table_name}--------')
            print(records[0])

        df = (pd.DataFrame.from_records((r['fields'] for r in records)))

        df_list[table_name] = df

    return df_list, df

def get_airtable_jobs(fields={}):
    if not fields:
        fields = {'B4-Trainees': ['Name', 'Email', 'Profile site Link', 'Public tags'],
                'Jobs': ['Title','Full description','Website (from Company)']}

    dflist, _ = get_table(['Jobs'], fields=fields)
    jobs = dflist['Jobs'].dropna(subset=['Full description'])

    return jobs

def get_airtable_profiles(fields={}):
    if not fields:
        fields = {'B4-Trainees': ['Name', 'Email', 'Profile site Link', 'Public tags'],
                'Jobs': ['Title','Full description','Website (from Company)']}

    dflist, _ = get_table(['B4-Trainees'], fields=fields)
    profiles = dflist['B4-Trainees'].dropna(subset=['Email'])

    return profiles
