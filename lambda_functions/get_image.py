import json
import base64
from config import get_s3_client, get_dynamodb_resource, S3_BUCKET_NAME, DYNAMODB_TABLE_NAME

def lambda_handler(event, context):
    try:
        path_params = event.get('pathParameters', {})
        image_id = path_params.get('image_id')
        
        query_params = event.get('queryStringParameters', {}) or {}
        download = query_params.get('download', 'false').lower() == 'true'
        
        if not image_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'image_id is required'})
            }
        
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        response = table.get_item(Key={'image_id': image_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Image not found'})
            }
        
        metadata = response['Item']
        
        # Convert DynamoDB Decimal types to int/float for JSON serialization
        for key, value in metadata.items():
            if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                if '.' in str(value):
                    metadata[key] = float(value)
                else:
                    metadata[key] = int(value)
            elif isinstance(value, float):
                metadata[key] = int(value)
        
        s3_client = get_s3_client()
        
        if download:
            s3_response = s3_client.get_object(
                Bucket=S3_BUCKET_NAME,
                Key=f"images/{image_id}"
            )
            
            image_data = s3_response['Body'].read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            result = {
                'image_id': image_id,
                'metadata': metadata,
                'image_data': image_base64,
                'content_type': 'image/jpeg'
            }
        else:
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': S3_BUCKET_NAME,
                    'Key': f"images/{image_id}"
                },
                ExpiresIn=3600
            )
            
            result = {
                'image_id': image_id,
                'metadata': metadata,
                'download_url': presigned_url,
                'expires_in': 3600
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }