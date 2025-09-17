import os
import boto3
from botocore.config import Config

AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'instagram-images-bucket')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'image-metadata')

LOCALSTACK_ENDPOINT = os.environ.get('LOCALSTACK_ENDPOINT', 'http://localhost:4566')

config = Config(
    region_name=AWS_REGION,
    signature_version='v4',
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

def get_s3_client():
    if os.environ.get('USE_LOCALSTACK', 'true').lower() == 'true':
        return boto3.client(
            's3',
            endpoint_url=LOCALSTACK_ENDPOINT,
            aws_access_key_id='test',
            aws_secret_access_key='test',
            config=config
        )
    return boto3.client('s3', config=config)

def get_dynamodb_client():
    if os.environ.get('USE_LOCALSTACK', 'true').lower() == 'true':
        return boto3.client(
            'dynamodb',
            endpoint_url=LOCALSTACK_ENDPOINT,
            aws_access_key_id='test',
            aws_secret_access_key='test',
            config=config
        )
    return boto3.client('dynamodb', config=config)

def get_dynamodb_resource():
    if os.environ.get('USE_LOCALSTACK', 'true').lower() == 'true':
        return boto3.resource(
            'dynamodb',
            endpoint_url=LOCALSTACK_ENDPOINT,
            aws_access_key_id='test',
            aws_secret_access_key='test',
            config=config
        )
    return boto3.resource('dynamodb', config=config)