#!/bin/bash

# 🚀 Sorbo Django Deployment Script
# This script automates the deployment process on your VPS

set -e  # Exit on any error

echo "🚀 Starting Sorbo Django Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/sorbo/sorbo_back"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="sorbo"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as sorbo user
if [ "$USER" != "sorbo" ]; then
    print_error "This script must be run as the 'sorbo' user"
    exit 1
fi

# Navigate to project directory
print_status "Navigating to project directory..."
cd "$PROJECT_DIR"

# Pull latest changes
print_status "Pulling latest changes from Git..."
git pull origin main

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install/update dependencies
print_status "Installing/updating Python dependencies..."
pip install -r sorbo_back/requirements.txt

# Run database migrations
print_status "Running database migrations..."
python manage.py migrate

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Restart the service
print_status "Restarting Django service..."
sudo systemctl restart $SERVICE_NAME

# Check service status
print_status "Checking service status..."
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    print_success "Service is running successfully!"
else
    print_error "Service failed to start!"
    sudo systemctl status $SERVICE_NAME
    exit 1
fi

# Test the application
print_status "Testing application endpoints..."
sleep 3  # Wait for service to fully start

# Test basic connectivity
if curl -s http://localhost:8000/api/products/ > /dev/null; then
    print_success "API is responding correctly!"
else
    print_warning "API test failed - check logs for details"
fi

print_success "Deployment completed successfully! 🎉"
print_status "Your Django application is now live at: http://$(curl -s ifconfig.me)/api/products/"

# Show recent logs
print_status "Recent application logs:"
sudo journalctl -u $SERVICE_NAME --no-pager -n 10
