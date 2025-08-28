#!/bin/bash

# 🔧 Python Version Fix Script for VPS
# This script helps fix Python version compatibility issues

echo "🔧 Checking Python version compatibility..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
print_status "Current Python version: $PYTHON_VERSION"

# Check if Python version is compatible
if [[ "$PYTHON_VERSION" < "3.8" ]]; then
    print_warning "Python version $PYTHON_VERSION is older than recommended (3.8+)"
    print_status "Django 3.2.25 should work with Python 3.6+"
    
    # Try to install with current Python version
    print_status "Attempting to install with current Python version..."
    
elif [[ "$PYTHON_VERSION" < "3.6" ]]; then
    print_error "Python version $PYTHON_VERSION is too old for Django 3.2"
    print_status "Upgrading Python to 3.8+..."
    
    # Install Python 3.8
    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.8 python3.8-venv python3.8-dev
    
    print_success "Python 3.8 installed successfully"
    print_status "Creating new virtual environment with Python 3.8..."
    
    # Remove old venv and create new one
    rm -rf venv
    python3.8 -m venv venv
    source venv/bin/activate
    
    print_success "New virtual environment created with Python 3.8"
else
    print_success "Python version $PYTHON_VERSION is compatible"
fi

# Install dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r sorbo_back/requirements.txt

if [ $? -eq 0 ]; then
    print_success "Dependencies installed successfully!"
else
    print_error "Failed to install dependencies"
    print_status "Trying alternative approach..."
    
    # Try installing without version pins
    pip install Django djangorestframework djangorestframework-simplejwt django-cors-headers stripe gunicorn psycopg2-binary python-dotenv requests
    
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed with latest compatible versions!"
    else
        print_error "Still failed to install dependencies"
        exit 1
    fi
fi

print_success "Python version compatibility fix completed!"
print_status "You can now continue with the deployment process."
