import io
import os
import pandas as pd
import boto3
import configparser
from botocore.exceptions import ClientError
from time import time


config_file_path = './project1-deploy-static-website/config.cfg'

config = configparser.ConfigParser()
config.read_file(open(config_file_path))

# read data from config.cfg file
KEY = config.get("AWS", "AWS_ACCESS_KEY_ID")
SECRET = config.get("AWS", "AWS_SECRET_ACCESS_KEY")

S3_BUCKET_OUTPUT = config.get("S3", "S3_BUCKET_OUTPUT")
S3_REGION = config.get("S3", "S3_REGION")


def get_session():
    """
    To get aws session
    OUTPUTs:
    Return session - to connect to aws s3 by KEY, SECRET, REGION
    """
     #Creating Session With Boto3.
    session = boto3.Session(
        aws_access_key_id=KEY,
        aws_secret_access_key=SECRET,
        region_name=S3_REGION
    )
    return session

def upload_file_to_s3(path_to_file, filename, output_folder=None, count_time=True):
    """
    Upload sepecific file/ folder to AWS S3
    INPUTS:
    * path_to_file: path to folder need to upload
    * filename: folder name need to upload
    * output_folder: defauft None mean upload specific file - Not None means create subfolder to copy files
    * count_time: default True to count execution time
    OUTPUTS:
    Return True/False
    REFER: https://www.developerfiles.com/upload-files-to-s3-with-python-keeping-the-original-folder-structure/
    """
    if count_time is True:
        t0 = time()
    s3_client = boto3.client(
        's3', 
        region_name=S3_REGION, 
        aws_access_key_id=KEY,
        aws_secret_access_key=SECRET
        )
    file_binary = open(path_to_file, "rb").read()
    file_as_binary = io.BytesIO(file_binary)
    if output_folder is None:
        key = filename
    else:
        key = output_folder + "/" +filename
    try:
        s3_client.upload_fileobj(file_as_binary, S3_BUCKET_OUTPUT, key)

        if count_time is True:
            print(f'= Uploading file [{filename}]')
            print('== Upload file DONE in {0:.2f} sec(s)\n'.format(time()-t0))
        else:
            print('== Upload file DONE')
    except ClientError as e:
        print(e)
        return False
    return True

def upload_all_file_to_s3(path_to_file, file_name):
    """
    Upload all file to AWS S3
    INPUTS:
    * path_to_file: path to folder need to upload
    * filename: folder name need to upload
    OUTPUTS:
    Return None
    REFER: https://www.developerfiles.com/upload-files-to-s3-with-python-keeping-the-original-folder-structure/
    """
    t0 = time()
    session = get_session()
    s3 = session.resource('s3')
    bucket = s3.Bucket(S3_BUCKET_OUTPUT)
    path = path_to_file + file_name

    for subdir, dirs, files in os.walk(path):
        output_folder = subdir.replace(path_to_file, '')
        for file in files:
            print(f'uploading file: [{file}] to s3 folder [{output_folder}]')
            full_path = os.path.join(subdir, file)
            upload_file_to_s3(full_path, file, output_folder, count_time=False)
    print('===> UPLOADED successfully in total time: {0:.2f} sec(s)\n'.format(time()-t0))

def upload_s3_by_aws_cli(relative_path_to_file, s3_bucket_name):
    try:
        t0 = time()
        bucket_url = f's3://{s3_bucket_name}/' 
        aws_cli= f'aws s3 cp {relative_path_to_file} {bucket_url} --recursive'
        print(aws_cli)
        os.system(aws_cli)
        print('===> UPLOADED successfully to ' + bucket_url + '\nin total time: {0:.2f} sec(s)\n'.format(time()-t0))
    except Exception as e:
        print(f'ERROR while executing aws cli: [{aws_cli}] - bucket url: [{bucket_url}] \n with error: {e}')


if __name__ == "__main__":
    # upload_file_to_s3('project1-deploy-static-website/udacity-starter-website/index.html', 'index.html')
    # upload_all_file_to_s3('./project1-deploy-static-website/udacity-starter-website/', 'css')
    # upload_all_file_to_s3('./project1-deploy-static-website/udacity-starter-website/', 'img')
    # upload_all_file_to_s3('./project1-deploy-static-website/udacity-starter-website/', 'vendor')        
    relative_path = 'project1-deploy-static-website/udacity-starter-website'   
    upload_s3_by_aws_cli(relative_path, S3_BUCKET_OUTPUT)
