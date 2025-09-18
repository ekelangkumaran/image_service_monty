import json
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda_functions'))

from delete_image import lambda_handler

class TestDeleteImage(unittest.TestCase):

    def test_delete_success(self):
        event = {'pathParameters': {'image_id': 'test_id'}}

        with patch('delete_image.get_dynamodb_resource') as mock_db, \
             patch('delete_image.get_s3_client') as mock_s3:

            mock_table = MagicMock()
            mock_table.get_item.return_value = {
                'Item': {'image_id': 'test_id', 'user_id': 'user123'}
            }
            mock_db.return_value.Table.return_value = mock_table

            response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 200)

    def test_delete_not_found(self):
        event = {'pathParameters': {'image_id': 'missing_id'}}

        with patch('delete_image.get_dynamodb_resource') as mock_db:
            mock_table = MagicMock()
            mock_table.get_item.return_value = {}
            mock_db.return_value.Table.return_value = mock_table

            response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 404)

if __name__ == '__main__':
    unittest.main()