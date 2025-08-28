#!/bin/bash

# 🛠️ VPS Initial Setup Script for Sorbo Django
# Run this script as root on your VPS

set -e  # Exit on any error

echo "🛠️ Starting VPS Setup for Sorbo Django..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
apt install -y python3 python3-pip python3-venv nginx git curl wget htop ufw

# Install system dependencies
print_status "Installing system dependencies..."
apt install -y build-essential libpq-dev python3-dev

# Create deployment user
print_status "Creating deployment user 'sorbo'..."
if id "sorbo" &>/dev/null; then
    print_warning "User 'sorbo' already exists"
else
    adduser --disabled-password --gecos "" sorbo
    usermod -aG sudo sorbo
    print_success "User 'sorbo' created successfully"
fi

# Configure firewall
print_status "Configuring firewall..."
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Configure Nginx
print_status "Configuring Nginx..."
systemctl enable nginx
systemctl start nginx

# Create project directory
print_status "Creating project directory..."
mkdir -p /home/sorbo/sorbo_back
chown sorbo:sorbo /home/sorbo/sorbo_back

# Set up environment variables
print_status "Setting up environment variables..."
cat >> /etc/environment << EOF

# Django Settings
DJANGO_SETTINGS_MODULE=sorbo_back.settings_production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
STRIPE_PUBLISHABLE_KEY=pk_live_51RwX1ZD5cS3MsYULZSr3llAYXLKnKilkngejZwXl2dsIcU6qDpA2C5AMb1X6ciq2WoJQLxEo9UBlZhuHPiOkchul00jygswABE
STRIPE_SECRET_KEY=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
FRONTEND_URL=https://yourdomain.com
EOF

# Create Gunicorn service file
print_status "Creating Gunicorn service..."
cat > /etc/systemd/system/sorbo.service << EOF
[Unit]
Description=Sorbo Django Application
After=network.target

[Service]
User=sorbo
Group=sorbo
WorkingDirectory=/home/sorbo/sorbo_back
Environment="PATH=/home/sorbo/sorbo_back/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=sorbo_back.settings_production"
ExecStart=/home/sorbo/sorbo_back/venv/bin/gunicorn --workers 2 --bind unix:/home/sorbo/sorbo_back/sorbo.sock sorbo_back.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
print_status "Creating Nginx configuration..."
cat > /etc/nginx/sites-available/sorbo << EOF
server {
    listen 80;
    server_name _;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/sorbo/sorbo_back;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/sorbo/sorbo_back/sorbo.sock;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/sorbo /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Remove default site

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx

# Create logs directory
mkdir -p /home/sorbo/sorbo_back/logs
chown sorbo:sorbo /home/sorbo/sorbo_back/logs

print_success "VPS setup completed successfully! 🎉"

print_status "Next steps:"
echo "1. Clone your repository:"
echo "   su - sorbo"
echo "   cd /home/sorbo"
echo "   git clone https://github.com/yourusername/sorbo_back.git"
echo ""
echo "2. Set up Python environment:"
echo "   cd sorbo_back"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r sorbo_back/requirements.txt"
echo ""
echo "3. Configure Django:"
echo "   cp sorbo_back/settings.py sorbo_back/settings_production.py"
echo "   # Edit settings_production.py with your domain/IP"
echo ""
echo "4. Run migrations:"
echo "   python manage.py migrate"
echo "   python manage.py collectstatic --noinput"
echo ""
echo "5. Start the service:"
echo "   sudo systemctl start sorbo"
echo "   sudo systemctl enable sorbo"
echo ""
echo "6. Test your application:"
echo "   curl http://$(curl -s ifconfig.me)/api/products/"

print_warning "Don't forget to:"
echo "- Update ALLOWED_HOSTS in settings_production.py"
echo "- Configure your domain DNS"
echo "- Set up SSL certificate with Certbot"
echo "- Update FRONTEND_URL in environment variables"
