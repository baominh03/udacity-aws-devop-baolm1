import boto3
import configparser
from time import time


config_file_path = './project1-deploy-static-website/config.cfg'

config = configparser.ConfigParser()
config.read_file(open(config_file_path))

# read data from config.cfg file
KEY = config.get("AWS", "AWS_ACCESS_KEY_ID")
SECRET = config.get("AWS", "AWS_SECRET_ACCESS_KEY")

S3_BUCKET_OUTPUT = config.get("S3", "S3_BUCKET_OUTPUT")
S3_REGION = config.get("S3", "S3_REGION")


def upload():
    t0 = time()
    gc_bucket=""
    google_access_key_id=""
    google_access_key_secret=""

    s3_client = boto3.client('s3',
                          region_name=S3_REGION,
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET)
    
    gcs_client = boto3.client('s3',
                        region_name="auto",
                        endpoint_url="https://storage.googleapis.com",
                        aws_access_key_id=google_access_key_id,
                        aws_secret_access_key=google_access_key_secret
                        )
    gcs_data = gcs_client.list_objects(Bucket=gc_bucket)
    for i in gcs_data['Contents']:
        print(f"Copying gcs file: [{i['Key']}] to AWS S3 bucket: [{S3_BUCKET_OUTPUT}]")
        file_to_transfer = gcs_client.get_object(Bucket=gc_bucket, Key=i['Key'])
        s3_client.upload_fileobj(file_to_transfer['Body'], S3_BUCKET_OUTPUT, Key=i['Key'])
    print('== Upload file DONE in {0:.2f} sec(s)\n'.format(time()-t0))


if __name__ == "__main__":
    upload()
