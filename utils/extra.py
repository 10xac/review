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
import awswrangler as wr


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

class s3_mixin(ABC):
    def __init__(self,
                 sep = None,
                 profile_name = None,
                 bucket_name = None,
                 bucket_input = None,
                 bucket_output = None,                  
                 rootdir = None,  
                 overwrite = 0,                 
                 verbose = 1,
                 **kwargs):

        #
        self.profile_name = profile_name
        self.sep = sep
        self.rootdir = rootdir
        self.verbose = verbose
        self.overwrite = overwrite
        self.bucket_name = bucket_name
        self.bucket_input = bucket_input
        self.bucket_output = bucket_output

        self.session = get_boto_session()
        
    def get_boto_session(**kwargs):
        profile_name = kwargs.get('profile_name',self.profile_name)
        session = boto3.session.Session(profile_name=profile_name)
        return session
  
    def date_path(self,day,**kwargs):
        #
        hour = kwargs.get('hour',None)
        dayasone = kwargs.get('dayasone',True)
        #
        if dayasone:
            p = day
        else:
            p = day.replace("-", "/")

        #add hour to date
        if hour is None:
            p = f'{p}/*'
        else:
            p = f'{p}/{hour}'

        return p
    
    def get_object_name(self,prefix=True, rootdir=True,
                        isinput=False,isoutput=False,
                        folder=None, basename=None, ext=None):

        #
        b = self.bucket_name
        if isoutput:
            b = self.bucket_output
        if isinput:
            b = self.bucket_input
       

        if self.mounted_in_cluster(b=b) and isoutput:
            ismounted = True
            if prefix:
                b = f'/mnt/{b}'

            if rootdir and not self.rootdir is None:
                if len(self.rootdir)>0:
                    b = f'{b}/{self.rootdir}'
        else:
            ismounted = False
            if prefix:
                b = f's3://{b}'

            if rootdir and not self.rootdir is None:
                if len(self.rootdir)>0:
                    b = f'{b}/{self.rootdir}'
            
        if not folder is None:
            b = osjoin(b,folder)


        if not basename is None:
            b = osjoin(b,basename)

        if not ext is None:
            b = osjoin(b,ext)

        if ismounted:
            if len(b.split('.'))>1:
                os.makedirs(os.path.dirname(b),exist_ok=True)
            else:
                os.makedirs(b,exist_ok=True)


        return b

                
    def mounted_in_cluster(self,bucket=None):
        if bucket is None:
            bucket = self.bucket_output
            
        def fpath(x): return os.path.exists(x)
        mounted_in_cluster = fpath(f'/mnt/{b}')
        return mounted_in_cluster

    def fix_s3_path(self,filename):
        fname = filename
        if not self.mounted_in_cluster():        
            if not filename.startswith('s3://'):
                if filename.startswith('/mnt'):
                    fname = filename.replace('/mnt','')
                    fname = f's3://{fname}'
                
        return fname
        
    def file_in_disk(self,filename,**kwargs):

        if not self.mounted_in_cluster():
            fname = self.fix_s3_path(fname)
            return wr.s3.does_object_exist(fname)
        else:
            return os.path.exists(filename)


    
    def files_from_pattern(self,pp,**kwargs):
        if not self.mounted_in_cluster():
            print('***patern to glob from s3**',pp)
            fname = self.fix_s3_path(pp)
            paths = wr.s3.glob(fname) #['s3://'+x for x in fs.glob(pp)]
        else:
            print('***patern to glob from local**',pp)
            paths = [x for x in glob.glob(pp)]

        print('***glob paths***:',paths)
        return paths

    
    def write_to_disk(self, filename, df, index=False, **kwargs):
        #
        fname = filename
        if not self.mounted_in_cluster():
            fname = self.fix_s3_path(pp)            

        ext = fname.split('.')[-1]

        if ext=='csv':
            df.to_csv(fname,index=False)
        elif ext=='pkl':
            df.to_pickle(fname)
        elif ext=='json':
            df.to_json(fname)
        else:
            df.to_csv(fname,index=False)
        
    def read_from_disk(self, filename, **kwargs):
        #
        fname = filename
        if not self.mounted_in_cluster():
            fname = self.fix_s3_path(pp)

        ext = fname.split('.')[-1]

        if ext=='csv':
            df = pd.read_csv(fname)
        elif ext=='pkl':
            df = pd.read_pickle(fname)
        elif ext=='json':
            df = pd.read_json(fname)
        else:
            df = pd.read_csv(fname)
        
        return df

    

    def get_sampled_paths(self,pp,**kwargs):
        '''
        Given an S3 path pattern pp, return all paths that match
        If the keyword subsample=True, return the largest size files.
        The number of files returned is determined by nfilesmax keyword
        '''

        subsample = kwargs.get('subsample',self.subsample)
        nfilesmax = kwargs.get('nfilesmax',self.nfilesmax)
        bytecutoff = kwargs.get('bytecutoff',self.bytecutoff)


        paths = ['s3://'+x for x in wr.glob(pp)]

        nfiles_all = len(paths)

        #apply sampling and byte filtering
        #Note: when s3fs cache is disabled, calculating size
        #in a list takes a lot of time. 
        kk = None
        paths_new = paths   
        
        #
        nfiles = len(paths_new)
        if nfilesmax>0:                
            nfilesmax = min([nfiles,nfilesmax])
        else:
            nfilesmax = nfiles

        if nfiles>0:
            #
            if subsample:                
                paths = paths_new[0:nfilesmax] #random.sample(paths,nfilesmax)
            else:
                paths = paths_new

            #
            if self.verbose>0:
                substring = f'bytecutoff>{bytecutoff} and sampling={subsample}: {len(paths)}'
                print(f'#Files to read after {substring} of {nfiles_all}')
                if not kk is None:
                    print(f'The largest and smallest file sizes are: {size_list.max()} & {size_list.min()} bytes')
                
            if self.verbose>2: print(paths[0])

        else:
            #
            if self.verbose>0:
                print('path pattern to read: ',pp)
                print(f'#Files to read: {nfiles_all}')
                if self.verbose>2 and nfiles_all>0: print(paths[0])


        #
        return paths    

