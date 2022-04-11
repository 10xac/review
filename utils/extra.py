import os, sys
import time
import json
from os.path import join as osjoin
from datetime import datetime
from datetime import timedelta
#
from functools import partial
import hashlib
from abc import ABC
import boto3

#
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)
    

from urllib.request import urlopen

def is_aws_instance():
    """Check if an instance is running on AWS."""
    result = False
    if os.path.exists('"/var/lib/cloud'):
        result=True
        
    return result

def file_mt_days(filename,today=datetime.today()):
    
    if os.path.exists(filename):
        #Get the modification time of each file
        t = os.stat(filename)[8]

        #Check how older the file is from today
        filetime = today - datetime.fromtimestamp(t)
        return filetime.days
    else:
        return 1e10
        
# when hashing skills extracted from file, consider timestamp file modified 
def hash_file_reference(filename):
    if os.path.exists(filename):
        mt = os.path.getmtime(filename)
        mts = time.strftime("%Y-%m-%d-%H", time.gmtime(mt))
    else:
        mt = time.today()
        mts = time.strftime("%Y-%m-%d-%H", mt)        
    content = f'{filename} {mt}'
    
    h = hashlib.sha1() # Construct a hash object 
    h.update(content.encode('utf-8')) # Update the hash using a bytes object
    hex = h.hexdigest() # hash value as a hex string
    return f'{mts}_{hex}' 


def list_read_write(item=[], fname='', rw='r'):
    if len(item)>0 and rw.startswith(('w','a')):
        if fname:
            with open(fname, rw) as filehandle:
                for l in item:
                    filehandle.write('%s\n' % l)
        else:
            print('fname key, the path to save list of length {len(item}, is not provided')
            
    if len(fname)>3 and rw=='r':

        # open file and read the content in a list
        with open(fname, rw) as filehandle:
            for line in filehandle:
                # remove linebreak which is the last character of the string
                item.append(line[:-1])

    return item

def get_cache_filename(filename,subdir='spacy_skills',ext='.txt'):
    '''
    Construct new cache filename based on input and file modifed time
    '''
    hashstr = hash_file_reference(filename)
    path, fname = os.path.split(filename)
    basename, _ = os.path.splitext(fname)
    os.makedirs(os.path.join(path, subdir),exist_ok=True)
    return os.path.join(path, subdir, f'{basename}_{hashstr}{ext}')

def pd_filter_with_dict(df,dfkv=None,**kwargs):
    #return particular subset of items

    if dfkv is None:
        return df

    if not dfkv:
        return df
    
    dflist = []
    for key, val in dfkv.items():
        if not isinstance(val,list):
            vlist=[val]
        else:
            vlist=val
        for v in vlist:
            try:
                dd = df.groupby(key).get_group(v)
                dflist.append(dd)
            except:
                pass
        
    #if all or one of them are there, return it
    if len(dflist)>0:
        return  pd.concat(dflist,sort=False)
    else:
        return pd.DataFrame()


def drop_uname_cols(df_data):
    if 'Unnamed: 0' in df_data.columns:
        df_data = df_data.drop('Unnamed: 0',axis=1)
    return df_data

def sort_by_oneofthem(df,clist,totype=None):
    for c in clist:
        if c in df.columns:
            if totype is not None: df[c] = df[c].astype(totype)
            df = df.sort_values(c)
            break
    return df

def parse_s3(s3_path):
    if not s3_path.startswith('s3://'):
        raise ValueError("invalid s3 path")
    ridx = s3_path.find('/', 5)
    if ridx == -1:
        ridx = None
    bucket = s3_path[5:ridx]
    s3_path = s3_path.rstrip('/')
    if ridx is None:
        key_prefix = ""
    else:
        key_prefix = s3_path[s3_path.find('/', 5):]
    return s3_path, bucket, key_prefix
