import json
import configparser
from time import time
from time import sleep
import boto3
from botocore.exceptions import ClientError


config_file_path = './project1-deploy-static-website/config.cfg'

config = configparser.ConfigParser()
config.read_file(open(config_file_path))


# read data from config.cfg file
KEY = config.get("AWS", "AWS_ACCESS_KEY_ID")
SECRET = config.get("AWS", "AWS_SECRET_ACCESS_KEY")

S3_BUCKET_OUTPUT = config.get("S3", "S3_BUCKET_OUTPUT")
S3_REGION = config.get("S3", "S3_REGION")

DELAY = int(config.get("DELAY", "DELAY_TIME"))
TIMEOUT = int(config.get("DELAY", "TIMEOUT"))

    
def create_distribution(s3_bucket_name, s3_region):
    """
    To create distribution static website from s3 to cloudfront
    INPUTS:
    * s3_bucket_name
    * s3_region
    OUTPUTS:
    save cloudfront ID, MATCH_ID DOMAIN_NAME, S3_DOMAIN to config.cfg
    Reutrn None
    """
    try:
        s3_domain_name = f'{s3_bucket_name}.s3-website-{s3_region}.amazonaws.com' 
        cf = boto3.client('cloudfront',
                          region_name=s3_region,
                          aws_access_key_id=KEY,
                          aws_secret_access_key=SECRET)

        # Read json file then modify
        with open('project1-deploy-static-website/aws_helper/cloudfront_custom.json', 'r+') as f:
            json_data = json.load(f)
            # Modify json file
            json_data['Origins']['Items'][0]['DomainName'] = s3_domain_name
            json_data['Origins']['Items'][0]['Id'] = s3_domain_name
            json_data['DefaultCacheBehavior']['TargetOriginId']= s3_domain_name
            f.seek(0)        # <--- should reset file position to the beginning.
            json.dump(json_data, f, indent=4)
            f.truncate()     # remove remaining part
        response = cf.create_distribution(
            DistributionConfig=json_data
        )

        cloudfront_id = response['Distribution']['Id']
        cloudfront_status = response['Distribution']['Status']
        print('status: ' + cloudfront_status)
        print('id: ' + cloudfront_id)

        # Check CloudFront status untill Deployed
        t0 = time()
        count = 1
        while cloudfront_status == 'InProgress':
            status_response = cf.get_distribution(
                Id=cloudfront_id
            )
            cloudfront_status = status_response['Distribution']['Status']
            print("Creating cloudfront - Status[{}]: [{}]\n".format(count, cloudfront_status))
            if cloudfront_status == 'Deployed':
                break
            elif time()-t0 > TIMEOUT:
                raise ValueError(
                    "Cloudfront creation time is too long, please double check to avoid wasting money in: {0:.2f} sec\n".format(time()-t0))
            print('Delay {} sec(s)\n'.format(str(DELAY)))
            sleep(DELAY)
            count = count + 1
        print("=== CLOUDFRONT DISTRIBUTION CREATED DONE in: {0:.2f} sec\n".format(time()-t0))
        print("cloudfront_status: [{}]\n".format(cloudfront_status))

        # write ID, MATCH_ID DOMAIN_NAME, S3_DOMAIN to config.cfg
        config.read(config_file_path)
        config.set('CLOUDFRONT', 'ID', status_response['Distribution']['Id'])
        config.set('CLOUDFRONT', 'MATCH_ID', status_response['ETag'])
        config.set('CLOUDFRONT', 'DOMAIN_NAME', status_response['Distribution']['DomainName'])
        config.set('S3', 'S3_DOMAIN', s3_domain_name)
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
    except ClientError as e:
        print(f'ERROR create Cloudfront distribution with error: {e}')
        exit()


if __name__ == "__main__":
    create_distribution(S3_BUCKET_OUTPUT, S3_REGION)
    config = configparser.ConfigParser()
    config.read_file(open(config_file_path))
    cf_domain = config.get("CLOUDFRONT", "DOMAIN_NAME")
    s3_domain = config.get("S3", "S3_DOMAIN")
    print('=== Access these url to check the result:\n{}\n{} \n{}'.format(cf_domain, s3_domain, s3_domain + '/index.html'))
    