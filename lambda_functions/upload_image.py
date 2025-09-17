import json
import base64
import uuid
from config import get_s3_client, get_dynamodb_resource, S3_BUCKET_NAME, DYNAMODB_TABLE_NAME

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        
        if 'image_data' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'image_data is required'})
            }
        
        image_id = str(uuid.uuid4())
        image_data = base64.b64decode(body['image_data'])
        
        metadata = {
            'image_id': image_id,
            'user_id': body.get('user_id', 'anonymous'),
            'tags': body.get('tags', '')
        }
        
        s3_client = get_s3_client()
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"images/{image_id}",
            Body=image_data,
            ContentType=body.get('content_type', 'image/jpeg'),
            Metadata={
                'user_id': metadata['user_id'],
                'tags': metadata['tags']
            }
        )
        
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        table.put_item(Item=metadata)
        
        response_body = {
            'message': 'Image uploaded successfully',
            'image_id': image_id,
            'metadata': metadata
        }
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body)
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