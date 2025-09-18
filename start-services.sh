#!/bin/bash
echo "Starting Image Service..."
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running."
    exit 1
fi
echo "Starting LocalStack..."
docker-compose up -d
echo "Waiting for LocalStack..."
sleep 10


echo "Setting up infrastructure..."
python scripts/setup_infrastructure.py
python scripts/deploy_lambda_functions.py
python scripts/create_api_gateway.py
