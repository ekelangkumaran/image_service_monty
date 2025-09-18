import json
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda_functions'))

from list_images import lambda_handler

class TestListImages(unittest.TestCase):

    def test_list_empty(self):
        event = {'queryStringParameters': None}

        with patch('list_images.get_dynamodb_resource') as mock_db:
            mock_table = MagicMock()
            mock_table.scan.return_value = {'Items': []}
            mock_db.return_value.Table.return_value = mock_table

            response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['count'], 0)

    def test_list_with_filter(self):
        event = {'queryStringParameters': {'user_id': 'test_user'}}

        with patch('list_images.get_dynamodb_resource') as mock_db:
            mock_table = MagicMock()
            mock_table.query.return_value = {
                'Items': [{'image_id': 'img1', 'user_id': 'test_user', 'tags': 'test'}]
            }
            mock_db.return_value.Table.return_value = mock_table

            response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['count'], 1)

if __name__ == '__main__':
    unittest.main()