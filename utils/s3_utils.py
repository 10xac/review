import os, sys
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)
    
    
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
import json

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


def list_files(bucket: str):
    """
    Function to list files in a given S3 bucket
    """
    s3 = boto3.client("s3")
    contents = []
    for item in s3.list_objects(Bucket=bucket)["Contents"]:
        contents.append(item)
    print(contents)
    return contents


def download_file(file_name: str, bucket: str, output: str):
    """
    Function to download a given file from an S3 bucket
    """
    s3 = boto3.resource("s3")
    s3.Bucket(bucket).download_file(file_name, output)
    print(f"{filename} downloaded successfully")

    return output

def get_s3_csv_dataframe(bucket: str, filename: str):
    """
    Function to get a dataframe an S3 bucket and key
    """   
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket, Key=filename)
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 200:
        print(f"Successful S3 get_object response. Status - {status}")
        df = pd.read_csv(response.get("Body"))
    else:
        print(f"Unsuccessful S3 get_object response. Status - {status}")
    return df

def get_s3_json_dataframe(bucket: str, filename: str):
    """
    Function to get a dataframe an S3 bucket and key
    """   
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket, Key=filename)
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    if status == 200:
        print(f"Successful S3 get_object response. Status - {status}")
        df = pd.read_json(response.get("Body"))
    else:
        print(f"Unsuccessful S3 get_object response. Status - {status}")
    return df


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
