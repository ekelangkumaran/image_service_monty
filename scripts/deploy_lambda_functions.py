#!/usr/bin/env python3

import boto3
import json
import os
import sys
import zipfile
import tempfile
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_functions.config import LOCALSTACK_ENDPOINT

AWS_REGION = 'us-east-1'
LAMBDA_RUNTIME = 'python3.9'
LAMBDA_TIMEOUT = 30
LAMBDA_MEMORY = 256

def get_lambda_client():
    return boto3.client(
        'lambda',
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name=AWS_REGION
    )

def create_deployment_package(function_name, lambda_dir):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
        with zipfile.ZipFile(tmp_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            function_file = os.path.join(lambda_dir, f"{function_name}.py")
            config_file = os.path.join(lambda_dir, "config.py")
            
            if os.path.exists(function_file):
                zip_file.write(function_file, f"{function_name}.py")
            if os.path.exists(config_file):
                zip_file.write(config_file, "config.py")
        
        return tmp_file.name

def deploy_lambda_function(lambda_client, function_name, handler, zip_file_path):
    try:
        with open(zip_file_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        try:
            response = lambda_client.create_function(
                FunctionName=function_name,
                Runtime=LAMBDA_RUNTIME,
                Role='arn:aws:iam::000000000000:role/lambda-role',
                Handler=handler,
                Code={'ZipFile': zip_content},
                Timeout=LAMBDA_TIMEOUT,
                MemorySize=LAMBDA_MEMORY,
                Environment={
                    'Variables': {
                        'AWS_REGION': AWS_REGION,
                        'USE_LOCALSTACK': 'true',
                        'LOCALSTACK_ENDPOINT': 'http://host.docker.internal:4566',
                        'S3_BUCKET_NAME': 'instagram-images-bucket',
                        'DYNAMODB_TABLE_NAME': 'image-metadata'
                    }
                }
            )
            
        except lambda_client.exceptions.ResourceConflictException:
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_content
            )
            
            
        return response
        
    except Exception as e:
        print(f"Error deploying {function_name}: {e}")
        return None

def create_lambda_role(lambda_client):
    iam_client = boto3.client(
        'iam',
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name=AWS_REGION
    )
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        iam_client.create_role(
            RoleName='lambda-role',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Path='/',
        )
        
    except Exception as e:
        print(f"Error creating lambda-role: {e}")

def main():
    lambda_client = get_lambda_client()
    create_lambda_role(lambda_client)
    
    functions = [
        ('upload_image', 'upload_image.lambda_handler'),
        ('list_images', 'list_images.lambda_handler'),
        ('get_image', 'get_image.lambda_handler'),
        ('delete_image', 'delete_image.lambda_handler')
    ]
    
    lambda_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lambda_functions')
    
    for function_name, handler in functions:
        zip_file_path = create_deployment_package(function_name, lambda_dir)
        
        result = deploy_lambda_function(lambda_client, function_name, handler, zip_file_path)
        
        os.unlink(zip_file_path)
        
        if result:
            print(f"  Function ARN: {result.get('FunctionArn', 'N/A')}")
    
    print("\nDeployed functions:")
    for function_name, _ in functions:
        print(f"  - {function_name}")

if __name__ == "__main__":
    main()