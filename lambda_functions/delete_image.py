import json
from config import get_s3_client, get_dynamodb_resource, S3_BUCKET_NAME, DYNAMODB_TABLE_NAME

def lambda_handler(event, context):
    try:
        path_params = event.get('pathParameters', {})
        image_id = path_params.get('image_id')
        
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
        
        s3_client = get_s3_client()
        s3_client.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"images/{image_id}"
        )
        
        table.delete_item(Key={'image_id': image_id})
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Image deleted successfully',
                'image_id': image_id
            })
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