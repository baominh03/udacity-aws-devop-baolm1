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


def config_static_website(s3_bucket_name):
    """
    config s3 static website
    INPUTS:
    * s3_bucket_name
    OUTPUTS:
    Reutrn None
    """
    try:
        t0 = time()
        s3 = boto3.client('s3',
                            region_name=S3_REGION,
                            aws_access_key_id=KEY,
                            aws_secret_access_key=SECRET)
        website_configuration = {
    'ErrorDocument': {'Key': 'index.html'},
    'IndexDocument': {'Suffix': 'index.html'},
        }

        # Set the website configuration
        s3.put_bucket_website(Bucket=s3_bucket_name,
                            WebsiteConfiguration=website_configuration)
        result = s3.get_bucket_website(Bucket=s3_bucket_name)
        print(result)
        print('=== Config S3 static website DONE for [' + s3_bucket_name + '] in: {0:.2f} sec(s)\n'.format(time()-t0))
        
    except ClientError as e:
        print.error('Config S3 static website failed: '+ e)
        exit()


if __name__ == "__main__":
    config_static_website(S3_BUCKET_OUTPUT)
