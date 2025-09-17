#!/bin/bash
set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
echo "📁 Project directory: $PROJECT_ROOT"
docker-compose up -d
python3 scripts/setup_infrastructure.py
python3 scripts/deploy_lambda_functions.py
python3 scripts/create_api_gateway.py
python3 -m pytest tests/ -v
echo "Setup completed"
