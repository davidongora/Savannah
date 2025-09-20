#!/bin/bash

echo "Build started..."

# Install dependencies
pip install -r requirements.txt

# Collect static files
cd savannah_test || exit
python manage.py collectstatic --noinput

echo "Build completed!"