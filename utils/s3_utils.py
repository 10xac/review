import boto3
import io
from io import StringIO
from io import BytesIO
import json
import pickle
import os
from botocore.exceptions import NoCredentialsError


from utils.tenx_logger import TenxLogger
logger = TenxLogger(os.path.basename(__file__))

if os.path.exists(".env/aws_config.json"):
    with open(".env/aws_config.json") as e:
        env = json.load(e)

    # Creating the low level functional client
    client = boto3.client(
        "s3",
        aws_access_key_id=env["aws_access_key_id"],
        aws_secret_access_key=env["aws_secret_access_key"],
        region_name=env["region_name"],
    )

    # Creating the high level object oriented interface
    resource = boto3.resource(
        "s3",
        aws_access_key_id=env["aws_access_key_id"],
        aws_secret_access_key=env["aws_secret_access_key"],
        region_name=env["region_name"],
    )

    # Fetch the list of existing buckets
    clientResponse = client.list_buckets()

def two_digit_str(xx):
    x = int(xx)
    if x < 10:
        return '0'+str(x)
    else:
        return str(x)
    
def get_s3_prefix(folder, year, month, day, hour):      
    
    PREFIX = folder
    
    if year:
        PREFIX = PREFIX + '/' + str(year)
    else:
        return PREFIX
        
    if month:            
        PREFIX = PREFIX + '-' + two_digit_str(month)
    else:
        return PREFIX            
        
    if day:            
        PREFIX = PREFIX + '-' + two_digit_str(day)
    else:
        return PREFIX
                
    if hour:
        PREFIX = PREFIX + ' ' + two_digit_str(hour)
    else:
        return PREFIX
                
    return PREFIX 
    
def create_filename(datetime_obj = None, ext: str = ".txt", 
                    prefix: str = "",  suffix: str = "" ):
    """
    Function to create a filename with a datetime stamp
    """
    if datetime_obj is None:
        datetime_obj = datetime.now()
        
    
    # convert datetime obj to string
    str_dt_obj = str(datetime_obj)
    
    # create a file object along with extension
    file_name = prefix + str_dt_obj + suffix + ext
    
    return file_name
    
def upload_file(local_file: str, bucket_name: str, s3_file_name: str):
    """
    Function to upload a file to an S3 bucket
    """

    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(local_file, bucket_name, s3_file_name)
        print(local_file + " uploaded successfully")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def list_files(bucket: str, **kwargs):
    """
    List files in a folder (prefix) in an S3 bucket.

    Args:
        folder_key (str): The key (prefix) of the folder in the S3 bucket.
        bucket_name (str): The name of the S3 bucket.

    Returns:
        list: List of file keys (paths) in the specified folder.
    """
    
    contents = []
    
    try:
        s3 = boto3.client("s3")
        # Use the paginator to retrieve the file paths for objects matching the prefix
        paginator = s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket, **kwargs)

        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    contents.append(obj['Key'])                                            
        
        return contents
    except Exception as e:
        print(f"Failed to list files in folder '{folder_key}': {e}")
        return []

def list_files_in_s3_folder(folder_key, bucket_name):
    return list_files(bucket_name, Prefix=folder_key)

    
def get_all_data(bucket, prefix, **kwargs):
    print(f'Getting data from S3 with filter bucket={bucket} and prefix={prefix} ..')
    filepaths = list_files(bucket, Prefix=prefix, MaxKeys=kwargs.get('maxkeys',2000) )
                    
    if kwargs.get('dataframe', True):
        df = get_s3_dataframe(bucket,  filepaths, ext=kwargs.get('ext','csv') )                
        return df    
    else:
        return filepaths

def download_file(file_name: str, bucket: str, output: str):
    """
    Function to download a given file from an S3 bucket
    """
    s3 = boto3.resource("s3")
    s3.Bucket(bucket).download_file(file_name, output)
    print(f"{filename} downloaded successfully")

    return output

def get_s3_dataframe(bucket: str, pathlist: "str | list[str]", ext='csv'):
    """
    Function to get a dataframe an S3 bucket and key
    """   
    if isinstance(pathlist, str):
        pathlist = [pathlist]
        
    
    s3_client = boto3.client("s3")
    
    dflist = []
    for filename in pathlist:
        response = s3_client.get_object(Bucket=bucket, Key=filename)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status == 200:
            if ext == 'csv':
                df = pd.read_csv(response.get("Body"))
            elif ext == 'json':
                df = pd.read_json(response.get("Body"))
            elif ext == 'parquet':
                df = pd.read_parquet(response.get("Body"))
            else:
                df = pd.read_csv(response.get("Body"))
                
            df['filename'] = filename
                
            dflist.append(df)
        else:
            print(f"Unsuccessful S3 get_object response. Status - {status}")
            
       
    dfall = pd.concat(dflist, ignore_index=True, sort=False)
    
    return dfall

def get_s3_csv_dataframe(bucket: str, filename: str):
    """
    Function to get a dataframe an S3 bucket and key
    """   
    return get_s3_dataframe(bucket, filename, ext='csv')

def get_s3_json_dataframe(bucket: str, filename: str):
    """
    Function to get a dataframe an S3 bucket and key
    """   
    return get_s3_dataframe(bucket, filename, ext='json')

def upload_dataframe_to_s3(dataframe, bucket_name, file_name):
    """
    Uploads a Pandas DataFrame directly to an S3 bucket as a CSV file.

    Args:
        dataframe (pandas.DataFrame): The DataFrame to upload.
        bucket_name (str): The name of the S3 bucket.
        file_name (str): The name of the file to be created in the bucket.
    """
    try:
        csv_buffer = io.StringIO()
        dataframe.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        csv_bytes = csv_buffer.getvalue().encode('utf-8')

        s3_client = boto3.client('s3')
        s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=csv_bytes)
  
        print(f"DataFrame uploaded to S3: {file_name}")
    except Exception as e:
        print(f"Upload failed: {e}")

def read_dataframe_from_s3(bucket_name, file_name):
    """
    Reads a CSV file from an S3 bucket into a Pandas DataFrame.

    Args:
        bucket_name (str): The name of the S3 bucket.
        file_name (str): The name of the file to be read from the bucket.

    Returns:
        pandas.DataFrame or None: The DataFrame containing the data from the CSV file,
                                  or None if an error occurred.
    """
    try:
        s3_client = boto3.client('s3')

        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        csv_content = response['Body'].read().decode('utf-8')

        dataframe = pd.read_csv(StringIO(csv_content))

        return dataframe
    except Exception as e:
        print(f"Error reading file from S3: {e}")
        return None
    
def file_exists_in_s3(bucket_name, file_key):
    """
    Checks if a file exists in an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        file_key (str): The key (path) of the file in the bucket.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    try:
        s3_client = boto3.client('s3')
        s3_client.head_object(Bucket=bucket_name, Key=file_key)
        return True
    except Exception as e:
        return False
    
def upload_file_to_s3(file_data, file_key, bucket_name):
    """
    Upload file data to an S3 bucket.

    Args:
        file_data (bytes): The binary data of the file to be uploaded.
        file_key (str): The key (path) of the file in the S3 bucket.
        bucket_name (str): The name of the S3 bucket.
    """
    try:
        s3_client = boto3.client('s3')

        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=file_data.encode('utf-8'))

        print(f"File uploaded to S3: {file_key}")
    except Exception as e:
        print(f"Upload failed: {e}")

def read_text_file_from_s3(file_key, bucket_name):
    """
    Read a text file from an S3 bucket.

    Args:
        file_key (str): The key (path) of the file in the S3 bucket.
        bucket_name (str): The name of the S3 bucket.

    Returns:
        str or None: The content of the file as a string, or None if the file doesn't exist or an error occurs.
    """
    try:
        s3_client = boto3.client('s3')

        file_buffer = BytesIO()
        s3_client.download_fileobj(bucket_name, file_key, file_buffer)
        file_buffer.seek(0)

        file_content = file_buffer.read().decode('utf-8')
        return file_content
    except Exception as e:
        print(f"Read failed: {e}")
        return None
    
    
def delete_file_from_s3(bucket_name, file_path):
    """
    Delete a file from an S3 bucket.
    """
    # Initialize S3 client
    s3 = boto3.client('s3')

    # Delete file from S3
    s3.delete_object(Bucket=bucket_name, Key=file_path)
    print("File deleted from S3.")
    

        


if __name__ == "__main__":
    foldername = "linkedlnScrapedJobs"
    filename = 'jdcrawl/2021-11-04 22:21:44.992922.csv'
    output = "newfile.csv"
    # Print the bucket names one by one
    # print('Printing bucket names...')
    # for bucket in clientResponse['Buckets']:
    #     print(f'Bucket Name: {bucket["Name"]}')

    upload_file(
        f"{filename}", "jobmodel", f"{foldername}/{filename}"
    )
    # download_file(f"{foldername}/{filename}", 'jobmodel', output)
