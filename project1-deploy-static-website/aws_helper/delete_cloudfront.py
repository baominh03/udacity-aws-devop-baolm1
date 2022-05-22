import json
import boto3
import configparser
from time import time
from time import sleep
from botocore.exceptions import ClientError

config_file_path = './project1-deploy-static-website/config.cfg'

config = configparser.ConfigParser()
config.read_file(open(config_file_path))


# read data from dwh.cfg file
KEY = config.get("AWS", "AWS_ACCESS_KEY_ID")
SECRET = config.get("AWS", "AWS_SECRET_ACCESS_KEY")

S3_BUCKET_OUTPUT = config.get("S3", "S3_BUCKET_OUTPUT")
S3_REGION = config.get("S3", "S3_REGION")

CLOUDFRONT_MATCH_ID = config.get("CLOUDFRONT", "MATCH_ID")
CLOUDFRONT_ID = config.get("CLOUDFRONT", "ID")

DELAY = int(config.get("DELAY", "DELAY_TIME"))
TIMEOUT = int(config.get("DELAY", "TIMEOUT"))

def disable_cloudfront_distribution(s3_bucket_name, s3_region):
    """
    To disable cloudfront distribution
    """
    try:
        s3_domain_name = f'{s3_bucket_name}.s3-website-{s3_region}.amazonaws.com' 
        cf = boto3.client('cloudfront',
                          region_name=s3_region,
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET)

        # Read json file then modify Enabled to False
        with open('project1-deploy-static-website/aws_helper/cloudfront_custom_disable.json', 'r+') as f:
            json_data = json.load(f)
            json_data['Origins']['Items'][0]['DomainName'] = s3_domain_name
            json_data['Origins']['Items'][0]['Id'] = s3_domain_name
            json_data['DefaultCacheBehavior']['TargetOriginId']= s3_domain_name
            f.seek(0)        # <--- should reset file position to the beginning.
            json.dump(json_data, f, indent=4)
            f.truncate()     # remove remaining part              
            
        response = cf.update_distribution(
                DistributionConfig=json_data, 
                Id=CLOUDFRONT_ID, 
                IfMatch=CLOUDFRONT_MATCH_ID)


        
        cloudfront_status = response['Distribution']['Status']
        print('status: ' + cloudfront_status)

         # Check CloudFront status untill Deployed
        t0 = time()
        count = 1
        while cloudfront_status == 'InProgress':
            status_response = cf.get_distribution(
                Id=CLOUDFRONT_ID
            )
            cloudfront_status = status_response['Distribution']['Status']
            print("Disable cloudfront - Status[{}]: [{}]\n".format(count, cloudfront_status))
            if cloudfront_status == 'Deployed':
                break
            elif time()-t0 > TIMEOUT:
                raise ValueError(
                    "Disable Cloudfront too long, please double check to avoid wasting money in: {0:.2f} sec\n".format(time()-t0))
            print('Delay {} sec(s)\n'.format(str(DELAY)))
            sleep(DELAY)
            count = count + 1
        print("=== DISABLE CLOUDFRONT DONE in: {0:.2f} sec\n".format(time()-t0))
        print("cloudfront_status: [{}]\n".format(cloudfront_status))

        cf.delete_distribution(Id=CLOUDFRONT_ID, IfMatch=status_response['ETag'])  

        print("=== COMPLETELY DELETE CLOUDFRONT  ID: {} - MATCH_ID: {} sec\n".format(CLOUDFRONT_ID, CLOUDFRONT_MATCH_ID))
            
                   
    except ClientError as e:
        print(f'ERROR delete Cloudfront distribution with error: {e}')
        exit()

    


if __name__ == "__main__":
    disable_cloudfront_distribution(S3_BUCKET_OUTPUT, S3_REGION)
