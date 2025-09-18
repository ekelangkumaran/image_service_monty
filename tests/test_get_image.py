import json
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda_functions'))

from get_image import lambda_handler

class TestGetImage(unittest.TestCase):

    def test_get_image_success(self):
        event = {'pathParameters': {'image_id': 'test_id'}}

        with patch('get_image.get_dynamodb_resource') as mock_db, \
             patch('get_image.get_s3_client') as mock_s3:

            mock_table = MagicMock()
            mock_table.get_item.return_value = {
                'Item': {'image_id': 'test_id', 'user_id': 'user123', 'tags': 'test'}
            }
            mock_db.return_value.Table.return_value = mock_table

            mock_s3_client = MagicMock()
            mock_s3_client.generate_presigned_url.return_value = 'http://presigned-url'
            mock_s3.return_value = mock_s3_client

            response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['image_id'], 'test_id')

    def test_image_not_found(self):
        event = {'pathParameters': {'image_id': 'missing_id'}}

        with patch('get_image.get_dynamodb_resource') as mock_db:
            mock_table = MagicMock()
            mock_table.get_item.return_value = {}
            mock_db.return_value.Table.return_value = mock_table

            response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 404)

if __name__ == '__main__':
    unittest.main()