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


def create_s3_bucket(s3_bucket_name, s3_region):
    """
    Create S3 bucket 
    OUTPUTS:
    * s3
    """
    try:
        t0 = time()
        s3 = boto3.client('s3',
                          region_name=s3_region,
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET)
        location = {'LocationConstraint': s3_region}
        s3.create_bucket(Bucket=s3_bucket_name,
                         CreateBucketConfiguration=location)

        print('CREATED S3 BUCKET [' + s3_bucket_name + '] at region ['+ s3_region+'] in: {0:.2f} sec(s)\n'.format(time()-t0))
    except ClientError as e:
        print.error('S3 creation failed: '+ e)
        exit()
    return s3


if __name__ == "__main__":
    create_s3_bucket(S3_BUCKET_OUTPUT, S3_REGION)
