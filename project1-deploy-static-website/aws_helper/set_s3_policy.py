import boto3
import configparser
from botocore.exceptions import ClientError
from time import time
import json


config_file_path = './project1-deploy-static-website/config.cfg'

config = configparser.ConfigParser()
config.read_file(open(config_file_path))


# read data from config.cfg file
KEY = config.get("AWS", "AWS_ACCESS_KEY_ID")
SECRET = config.get("AWS", "AWS_SECRET_ACCESS_KEY")

S3_BUCKET_OUTPUT = config.get("S3", "S3_BUCKET_OUTPUT")
S3_REGION = config.get("S3", "S3_REGION")


def set_s3_policy(s3_bucket_name):
    """
    Set s3 policy
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
        # Create a bucket policy
        bucket_name = 'BUCKET_NAME'
        bucket_policy = {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Sid": "AddPerm",
                                    "Effect": "Allow",
                                    "Principal": "*",
                                    "Action": [
                                        "s3:GetObject"
                                    ],
                                    "Resource": [
                                        "arn:aws:s3:::" + s3_bucket_name +"/*"
                                    ]
                                }
                            ]
                        }
        # Convert the policy from JSON dict to string
        bucket_policy = json.dumps(bucket_policy)
        print(bucket_policy)

        # Set the new policy
        s3.put_bucket_policy(Bucket=s3_bucket_name, Policy=bucket_policy)
        print('=== Secure Bucket via IAM policy DONE for [' + s3_bucket_name + '] in: {0:.2f} sec(s)\n'.format(time()-t0))
    except ClientError as e:
        print.error('Secure Bucket via IAM policy failed: '+ e)
        exit()


if __name__ == "__main__":
    set_s3_policy(S3_BUCKET_OUTPUT)
