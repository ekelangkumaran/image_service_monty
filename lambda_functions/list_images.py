import json
from boto3.dynamodb.conditions import Key, Attr
from config import get_dynamodb_resource, DYNAMODB_TABLE_NAME

def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters', {}) or {}
        
        user_id = query_params.get('user_id')
        tags = query_params.get('tags')
        limit = int(query_params.get('limit', 20))
        last_evaluated_key = query_params.get('last_evaluated_key')
        
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        scan_kwargs = {
            'Limit': min(limit, 100)
        }
        
        filter_expression = None
        
        if user_id and tags:
            response = table.query(
                IndexName='UserIdIndex',
                KeyConditionExpression=Key('user_id').eq(user_id),
                FilterExpression=Attr('tags').contains(tags),
                Limit=limit
            )
        elif user_id:
            response = table.query(
                IndexName='UserIdIndex',
                KeyConditionExpression=Key('user_id').eq(user_id),
                Limit=limit
            )
        elif tags:
            response = table.query(
                IndexName='TagsIndex',
                KeyConditionExpression=Key('tags').eq(tags),
                Limit=limit
            )
        else:
            if last_evaluated_key:
                scan_kwargs['ExclusiveStartKey'] = json.loads(last_evaluated_key)

            response = table.scan(**scan_kwargs)
        
        items = response.get('Items', [])
        
        # Convert DynamoDB Decimal types to int/float for JSON serialization
        for item in items:
            for key, value in item.items():
                if hasattr(value, '__class__') and value.__class__.__name__ == 'Decimal':
                    if '.' in str(value):
                        item[key] = float(value)
                    else:
                        item[key] = int(value)
                elif isinstance(value, float):
                    item[key] = int(value)
        
        result = {
            'images': items,
            'count': len(items),
            'filters_applied': {
                'user_id': user_id,
                'tags': tags
            }
        }
        
        if 'LastEvaluatedKey' in response:
            result['last_evaluated_key'] = json.dumps(response['LastEvaluatedKey'])
        
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