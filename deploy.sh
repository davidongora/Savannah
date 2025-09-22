#!/bin/bash

# Deployment script for Savannah Customer Orders API
# This script deploys the Django application to the VPS server

set -e  # Exit on any error

# Configuration
SERVER_USER="root"
SERVER_HOST="185.240.51.176"
SERVER_PATH="/var/www/savannah/savannah_test"
LOCAL_PATH="./savannah_test"

echo "🚀 Starting deployment to $SERVER_HOST..."

# Function to run commands on the server
run_remote() {
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST "$1"
}

# Function to copy files to server
copy_to_server() {
    echo "📁 Copying files to server..."
    
    # Copy main Django project files
    scp -r -o StrictHostKeyChecking=no \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        $LOCAL_PATH/* $SERVER_USER@$SERVER_HOST:$SERVER_PATH/
        
    # Copy requirements.txt to parent directory
    scp -o StrictHostKeyChecking=no requirements.txt $SERVER_USER@$SERVER_HOST:/var/www/savannah/
    
    echo "✅ Files copied successfully"
}

# Function to install dependencies
install_dependencies() {
    echo "📦 Installing/updating dependencies..."
    run_remote "cd /var/www/savannah && pip3 install -r requirements.txt --quiet"
    echo "✅ Dependencies installed"
}

# Function to restart Django service
restart_service() {
    echo "🔄 Restarting Django service..."
    
    # Kill existing Django processes
    run_remote "pkill -f 'python3 manage.py runserver' || true"
    
    # Wait a moment for processes to stop
    sleep 2
    
    # Start Django service
    run_remote "cd $SERVER_PATH && nohup python3 manage.py runserver 0.0.0.0:8003 > /dev/null 2>&1 &"
    
    # Wait for service to start
    sleep 3
    
    echo "✅ Django service restarted"
}

# Function to check if service is running
check_service() {
    echo "🔍 Checking if service is running..."
    
    # Try to connect to the service
    if run_remote "curl -s -o /dev/null -w '%{http_code}' http://localhost:8003/api/auth/oidc-info/" | grep -q "200"; then
        echo "✅ Service is running successfully"
        echo "🌐 Application is available at: http://$SERVER_HOST:8003"
    else
        echo "⚠️  Service may not be responding properly"
        echo "🔧 Check logs: ssh $SERVER_USER@$SERVER_HOST 'cd $SERVER_PATH && tail -f nohup.out'"
    fi
}

# Main deployment function
main() {
    echo "=== Savannah API Deployment ==="
    echo "Target: $SERVER_USER@$SERVER_HOST:$SERVER_PATH"
    echo "================================"
    
    # Step 1: Copy files
    copy_to_server
    
    # Step 2: Install dependencies
    install_dependencies
    
    # Step 3: Restart service
    restart_service
    
    # Step 4: Check service status
    check_service
    
    echo ""
    echo "🎉 Deployment completed!"
    echo "📊 API Documentation: http://$SERVER_HOST:8003/api/"
    echo "🔐 OIDC Info: http://$SERVER_HOST:8003/api/auth/oidc-info/"
    echo ""
}

# Run deployment
main