# 🚀 Django VPS Deployment Guide

## 📋 Prerequisites

### VPS Requirements:
- **OS**: Ubuntu 20.04/22.04 LTS (recommended)
- **Resources**: 1 vCPU, 4GB RAM (as discussed)
- **Storage**: 20GB+ SSD
- **Domain**: Optional but recommended

### Local Requirements:
- Git repository with your code
- SSH access to VPS
- Domain DNS configured (if using domain)

## 🔧 Step 1: VPS Initial Setup

### Connect to your VPS:
```bash
ssh root@your_vps_ip
```

### Update system:
```bash
apt update && apt upgrade -y
```

### Create deployment user:
```bash
adduser sorbo
usermod -aG sudo sorbo
su - sorbo
```

## 🐍 Step 2: Install Python & Dependencies

### Install Python and tools:
```bash
sudo apt install python3 python3-pip python3-venv nginx git curl -y
```

### Install system dependencies:
```bash
sudo apt install build-essential libpq-dev python3-dev -y
```

## 📁 Step 3: Clone Your Project

### Clone your repository:
```bash
cd /home/sorbo
git clone https://github.com/yourusername/sorbo_back.git
cd sorbo_back
```

### Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Python dependencies:
```bash
pip install -r sorbo_back/requirements.txt
pip install gunicorn psycopg2-binary
```

## ⚙️ Step 4: Configure Django for Production

### Create production settings:
```bash
cp sorbo_back/settings.py sorbo_back/settings_production.py
```

### Edit production settings (see `settings_production.py` file below)

### Set environment variables:
```bash
sudo nano /etc/environment
```

Add these lines:
```bash
DJANGO_SETTINGS_MODULE=sorbo_back.settings_production
SECRET_KEY=your_very_secure_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_51RwX1ZD5cS3MsYULZSr3llAYXLKnKilkngejZwXl2dsIcU6qDpA2C5AMb1X6ciq2WoJQLxEo9UBlZhuHPiOkchul00jygswABE
STRIPE_SECRET_KEY=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
FRONTEND_URL=https://yourdomain.com
```

## 🗄️ Step 5: Database Setup

### For SQLite (current setup):
```bash
cd /home/sorbo/sorbo_back
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

### For PostgreSQL (recommended for production):
```bash
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres createuser sorbo
sudo -u postgres createdb sorbo_db
sudo -u postgres psql -c "ALTER USER sorbo PASSWORD 'your_db_password';"
```

## 🔐 Step 6: Security Configuration

### Create Django superuser:
```bash
python manage.py createsuperuser
```

### Set proper permissions:
```bash
sudo chown -R sorbo:sorbo /home/sorbo/sorbo_back
chmod 755 /home/sorbo/sorbo_back
```

## 🌐 Step 7: Configure Gunicorn

### Create Gunicorn service file:
```bash
sudo nano /etc/systemd/system/sorbo.service
```

Add this content:
```ini
[Unit]
Description=Sorbo Django Application
After=network.target

[Service]
User=sorbo
Group=sorbo
WorkingDirectory=/home/sorbo/sorbo_back
Environment="PATH=/home/sorbo/sorbo_back/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=sorbo_back.settings_production"
ExecStart=/home/sorbo/sorbo_back/venv/bin/gunicorn --workers 3 --bind unix:/home/sorbo/sorbo_back/sorbo.sock sorbo_back.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Start and enable the service:
```bash
sudo systemctl start sorbo
sudo systemctl enable sorbo
sudo systemctl status sorbo
```

## 🚀 Step 8: Configure Nginx

### Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/sorbo
```

Add this content:
```nginx
server {
    listen 80;
    server_name your_vps_ip_or_domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/sorbo/sorbo_back;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/sorbo/sorbo_back/sorbo.sock;
    }
}
```

### Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/sorbo /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Step 9: SSL Certificate (Optional but Recommended)

### Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Get SSL certificate:
```bash
sudo certbot --nginx -d yourdomain.com
```

## 📊 Step 10: Monitoring & Logs

### Check application status:
```bash
sudo systemctl status sorbo
sudo systemctl status nginx
```

### View logs:
```bash
sudo journalctl -u sorbo -f
sudo tail -f /var/log/nginx/error.log
```

## 🔄 Step 11: Deployment Script

### Create deployment script:
```bash
nano /home/sorbo/deploy.sh
```

Add this content:
```bash
#!/bin/bash
cd /home/sorbo/sorbo_back
git pull origin main
source venv/bin/activate
pip install -r sorbo_back/requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart sorbo
echo "Deployment completed!"
```

### Make it executable:
```bash
chmod +x /home/sorbo/deploy.sh
```

## 🧪 Step 12: Testing

### Test your API endpoints:
```bash
curl http://your_vps_ip/api/products/
curl http://your_vps_ip/api/orders/
```

### Test Stripe integration:
```bash
# Create a test order
curl -X POST http://your_vps_ip/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "your_product_id",
    "client_name": "Test User",
    "client_email": "test@example.com",
    "client_phone": "1234567890",
    "client_address": "Test Address",
    "currency": "MXN"
  }'
```

## 🔧 Troubleshooting

### Common issues:

1. **Permission denied errors:**
   ```bash
   sudo chown -R sorbo:sorbo /home/sorbo/sorbo_back
   ```

2. **Port 80 already in use:**
   ```bash
   sudo systemctl stop apache2  # if Apache is running
   ```

3. **Database connection issues:**
   ```bash
   python manage.py check --database default
   ```

4. **Static files not loading:**
   ```bash
   python manage.py collectstatic --noinput
   sudo systemctl restart nginx
   ```

## 📈 Performance Optimization

### For 1 vCPU + 4GB setup:

1. **Optimize Gunicorn workers:**
   ```bash
   # In sorbo.service, use 2-3 workers
   --workers 2
   ```

2. **Enable Nginx caching:**
   ```nginx
   location /static/ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

3. **Database optimization:**
   ```python
   # Add to settings_production.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
           'OPTIONS': {
               'timeout': 20,
           }
       }
   }
   ```

## 🎯 Next Steps

1. **Set up monitoring** (optional):
   - Install htop: `sudo apt install htop`
   - Monitor resources: `htop`

2. **Set up backups:**
   ```bash
   # Backup database
   cp /home/sorbo/sorbo_back/db.sqlite3 /home/sorbo/backup/
   ```

3. **Set up CI/CD** (optional):
   - GitHub Actions
   - Automated deployments

4. **Scale when needed:**
   - Upgrade to 2 vCPU + 8GB
   - Migrate to PostgreSQL
   - Add Redis caching

## ✅ Deployment Checklist

- [ ] VPS provisioned and accessible
- [ ] Python and dependencies installed
- [ ] Project cloned and configured
- [ ] Production settings configured
- [ ] Database migrated
- [ ] Gunicorn service running
- [ ] Nginx configured and running
- [ ] SSL certificate installed (optional)
- [ ] API endpoints tested
- [ ] Stripe integration tested
- [ ] Monitoring set up
- [ ] Backups configured

## 🆘 Support

If you encounter issues:

1. Check logs: `sudo journalctl -u sorbo -f`
2. Verify services: `sudo systemctl status sorbo nginx`
3. Test connectivity: `curl http://localhost:8000/api/products/`
4. Check permissions: `ls -la /home/sorbo/sorbo_back/`

Your Django application should now be running on your VPS! 🚀
