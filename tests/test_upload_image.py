import json
import base64
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda_functions'))

from upload_image import lambda_handler

class TestUploadImage(unittest.TestCase):

    def test_upload_success(self):
        event = {
            'body': json.dumps({
                'image_data': base64.b64encode(b"test_image").decode(),
                'user_id': 'user123',
                'tags': 'test,photo'
            })
        }

        with patch('upload_image.get_s3_client'), \
             patch('upload_image.get_dynamodb_resource'):
            response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 201)
        body = json.loads(response['body'])
        self.assertIn('image_id', body)

    def test_missing_image_data(self):
        event = {'body': json.dumps({'user_id': 'user123'})}

        response = lambda_handler(event, {})

        self.assertEqual(response['statusCode'], 400)

if __name__ == '__main__':
    unittest.main()