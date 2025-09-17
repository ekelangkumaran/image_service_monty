#!/usr/bin/env python3

import boto3
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lambda_functions.config import LOCALSTACK_ENDPOINT, AWS_REGION

def get_api_gateway_client():
    return boto3.client(
        'apigateway',
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name=AWS_REGION
    )

def create_api_gateway():
    client = get_api_gateway_client()
    
    try:
        response = client.create_rest_api(
            name='instagram-image-service',
            description='Instagram-like image service API',
            endpointConfiguration={'types': ['REGIONAL']}
        )
        api_id = response['id']
        print(f"########REST API with ID: {api_id}")
        
        resources = client.get_resources(restApiId=api_id)
        root_resource_id = None
        for resource in resources['items']:
            if resource['path'] == '/':
                root_resource_id = resource['id']
                break
        
        images_resource = client.create_resource(
            restApiId=api_id,
            parentId=root_resource_id,
            pathPart='images'
        )
        images_resource_id = images_resource['id']
    
        
        image_id_resource = client.create_resource(
            restApiId=api_id,
            parentId=images_resource_id,
            pathPart='{image_id}'
        )
        image_id_resource_id = image_id_resource['id']
        
        
        methods = [
            {
                'resource_id': images_resource_id,
                'http_method': 'POST',
                'function_name': 'upload_image',
                'description': 'Upload image with metadata'
            },
            {
                'resource_id': images_resource_id,
                'http_method': 'GET',
                'function_name': 'list_images',
                'description': 'List images with filters'
            },
            {
                'resource_id': image_id_resource_id,
                'http_method': 'GET',
                'function_name': 'get_image',
                'description': 'Get/download image'
            },
            {
                'resource_id': image_id_resource_id,
                'http_method': 'DELETE',
                'function_name': 'delete_image',
                'description': 'Delete image'
            }
        ]
        
        for method_config in methods:
            
            
            client.put_method(
                restApiId=api_id,
                resourceId=method_config['resource_id'],
                httpMethod=method_config['http_method'],
                authorizationType='NONE',
                requestParameters={}
            )
            
            integration_uri = f"arn:aws:apigateway:{AWS_REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:{AWS_REGION}:000000000000:function:{method_config['function_name']}/invocations"
            
            client.put_integration(
                restApiId=api_id,
                resourceId=method_config['resource_id'],
                httpMethod=method_config['http_method'],
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=integration_uri,
                passthroughBehavior='WHEN_NO_MATCH'
            )
            
            client.put_method_response(
                restApiId=api_id,
                resourceId=method_config['resource_id'],
                httpMethod=method_config['http_method'],
                statusCode='200',
                responseModels={'application/json': 'Empty'},
                responseParameters={
                    'method.response.header.Access-Control-Allow-Origin': False
                }
            )
            
            client.put_integration_response(
                restApiId=api_id,
                resourceId=method_config['resource_id'],
                httpMethod=method_config['http_method'],
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                }
            )
            
            
        
        for resource_id in [images_resource_id, image_id_resource_id]:
            client.put_method(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                authorizationType='NONE'
            )
            
            client.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                type='MOCK',
                requestTemplates={'application/json': '{"statusCode": 200}'}
            )
            
            client.put_method_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': False,
                    'method.response.header.Access-Control-Allow-Methods': False,
                    'method.response.header.Access-Control-Allow-Origin': False
                }
            )
            
            client.put_integration_response(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,POST,DELETE,OPTIONS'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                }
            )
        
        
        
        deployment = client.create_deployment(
            restApiId=api_id,
            stageName='dev',
            description='Development stage deployment'
        )
        
        
        
        api_url = f"{LOCALSTACK_ENDPOINT}/restapis/{api_id}/dev/_user_request_"
        print(f"API Gateway deployed.\nAPI ID: {api_id}\nBase URL: {api_url}")
        # Endpoints:"
        #   POST   {api_url}/images
        #   GET    {api_url}/images
        #   GET    {api_url}/images/{id}
        #   DELETE {api_url}/images/{id}
        
        return api_id, api_url
        
    except Exception as e:
        print(f"Error creating API Gateway: {e}")
        return None, None

def main():
    api_id, api_url = create_api_gateway()
    
    if not api_id:
        print("API Gateway setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()