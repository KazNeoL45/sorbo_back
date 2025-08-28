# 🚀 Quick Deployment Reference

## 📋 Pre-Deployment Checklist

- [ ] VPS with Ubuntu 20.04/22.04 LTS
- [ ] SSH access to VPS
- [ ] Git repository with your code
- [ ] Domain name (optional but recommended)
- [ ] Stripe production keys ready

## 🔧 Initial VPS Setup (One-time)

### 1. Connect to VPS
```bash
ssh root@your_vps_ip
```

### 2. Run setup script
```bash
# Upload vps_setup.sh to your VPS first
chmod +x vps_setup.sh
./vps_setup.sh
```

### 3. Clone your project
```bash
su - sorbo
cd /home/sorbo
git clone https://github.com/yourusername/sorbo_back.git
cd sorbo_back
```

### 4. Set up Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r sorbo_back/requirements.txt
```

### 5. Configure Django
```bash
cp sorbo_back/settings.py sorbo_back/settings_production.py
# Edit settings_production.py with your domain/IP
nano sorbo_back/settings_production.py
```

### 6. Initialize database
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 7. Start services
```bash
sudo systemctl start sorbo
sudo systemctl enable sorbo
```

## 🔄 Regular Deployment

### Quick deployment (after setup)
```bash
su - sorbo
cd /home/sorbo/sorbo_back
./deploy.sh
```

### Manual deployment
```bash
su - sorbo
cd /home/sorbo/sorbo_back
git pull origin main
source venv/bin/activate
pip install -r sorbo_back/requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart sorbo
```

## 🔍 Monitoring & Troubleshooting

### Check service status
```bash
sudo systemctl status sorbo
sudo systemctl status nginx
```

### View logs
```bash
# Django logs
sudo journalctl -u sorbo -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Application logs
tail -f /home/sorbo/sorbo_back/logs/django.log
```

### Test endpoints
```bash
# Test API
curl http://your_vps_ip/api/products/
curl http://your_vps_ip/api/orders/

# Test from external
curl http://$(curl -s ifconfig.me)/api/products/
```

### Restart services
```bash
sudo systemctl restart sorbo
sudo systemctl restart nginx
```

## 🔒 SSL Setup (Optional)

### Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Get SSL certificate
```bash
sudo certbot --nginx -d yourdomain.com
```

## 📊 Performance Monitoring

### Check resource usage
```bash
htop
df -h
free -h
```

### Check application performance
```bash
# Check Gunicorn workers
ps aux | grep gunicorn

# Check Nginx connections
sudo netstat -tlnp | grep :80
```

## 🛠️ Common Commands

### Database operations
```bash
# Backup database
cp /home/sorbo/sorbo_back/db.sqlite3 /home/sorbo/backup/

# Restore database
cp /home/sorbo/backup/db.sqlite3 /home/sorbo/sorbo_back/
sudo systemctl restart sorbo
```

### Update dependencies
```bash
source venv/bin/activate
pip install --upgrade -r sorbo_back/requirements.txt
sudo systemctl restart sorbo
```

### Check configuration
```bash
# Test Django settings
python manage.py check --deploy

# Test Nginx config
sudo nginx -t
```

## 🚨 Emergency Procedures

### If service won't start
```bash
# Check logs
sudo journalctl -u sorbo -n 50

# Check permissions
ls -la /home/sorbo/sorbo_back/
sudo chown -R sorbo:sorbo /home/sorbo/sorbo_back/

# Restart from scratch
sudo systemctl stop sorbo
sudo systemctl start sorbo
```

### If Nginx issues
```bash
# Check Nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### If database issues
```bash
# Check database
python manage.py check --database default

# Reset migrations (if needed)
python manage.py migrate --fake-initial
```

## 📞 Support Commands

### System information
```bash
# OS version
lsb_release -a

# Python version
python3 --version

# Django version
python manage.py --version

# Installed packages
pip list
```

### Network information
```bash
# VPS IP
curl ifconfig.me

# Open ports
sudo netstat -tlnp

# Firewall status
sudo ufw status
```

## 🎯 Success Indicators

✅ **Service running**: `sudo systemctl is-active sorbo` returns "active"
✅ **Nginx running**: `sudo systemctl is-active nginx` returns "active"
✅ **API responding**: `curl http://your_vps_ip/api/products/` returns JSON
✅ **SSL working**: `curl -I https://yourdomain.com/api/products/` returns 200
✅ **Logs clean**: No errors in `sudo journalctl -u sorbo -n 20`

## 📝 Important Files

- **Settings**: `/home/sorbo/sorbo_back/sorbo_back/settings_production.py`
- **Service**: `/etc/systemd/system/sorbo.service`
- **Nginx**: `/etc/nginx/sites-available/sorbo`
- **Logs**: `/home/sorbo/sorbo_back/logs/django.log`
- **Database**: `/home/sorbo/sorbo_back/db.sqlite3`
- **Environment**: `/etc/environment`

Your Django application is now production-ready! 🚀
