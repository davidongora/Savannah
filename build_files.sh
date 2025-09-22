#!/bin/bash

echo "Build started..."

# Install dependencies
pip install -r requirements.txt

# Set minimal environment variables for build
export DEBUG="True"
export SECRET_KEY="build-time-secret-key"
export POSTGRES_DB="dummy"
export POSTGRES_USER="dummy"
export POSTGRES_PASSWORD="dummy"
export POSTGRES_HOST="localhost"

# Collect static files (this should not require database connection)
cd savannah_test || exit
python manage.py collectstatic --noinput --verbosity=2

echo "Build completed!"