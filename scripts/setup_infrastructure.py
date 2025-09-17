#!/usr/bin/env python3

import boto3
import os
import sys
from botocore.exceptions import ClientError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_functions.config import get_s3_client, get_dynamodb_client, S3_BUCKET_NAME, DYNAMODB_TABLE_NAME

def create_s3_bucket():
    s3_client = get_s3_client()
    
    try:
        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
        s3_client.put_bucket_cors(
            Bucket=S3_BUCKET_NAME,
            CORSConfiguration={
                'CORSRules': [{
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                    'AllowedOrigins': ['*'],
                    'MaxAgeSeconds': 3000
                }]
            }
        )
    except ClientError as e:
        print(f"Error creating bucket: {e}")
        raise

def create_dynamodb_table():
    dynamodb_client = get_dynamodb_client()
    
    try:
        response = dynamodb_client.create_table(
            TableName=DYNAMODB_TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'image_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'image_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'upload_timestamp',
                    'AttributeType': 'N'
                },
                {
                    'AttributeName': 'tags',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'UserIdIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'upload_timestamp',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                },
                {
                    'IndexName': 'TagsIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'tags',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'upload_timestamp',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except Exception as e:
        print(f"✗ Error creating table: {e}")
        raise

def main():    
    create_s3_bucket()
    create_dynamodb_table()
    
if __name__ == "__main__":
    main()