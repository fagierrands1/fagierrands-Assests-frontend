# FagiCRM - cPanel Deployment Guide

## Quick Start Guide for fagicrm.fagitone.com

This guide will help you deploy the FagiCRM application to cPanel hosting.

---

## Prerequisites

- cPanel hosting account with Python support (Python 3.8+)
- MySQL database access
- Domain: `fagicrm.fagitone.com` configured in cPanel
- SSH access (recommended) or File Manager access

---

## Step 1: Create MySQL Database

1. **Login to cPanel**
2. **Go to "MySQL Databases"**
3. **Create a new database:**
   - Database name: `fagicrm` (will become `yourusername_fagicrm`)
   - Click "Create Database"

4. **Create a database user:**
   - Username: `fagicrm_user` (will become `yourusername_fagicrm_user`)
   - Password: Generate a strong password (save it!)
   - Click "Create User"

5. **Add user to database:**
   - Select the user and database you just created
   - Grant **ALL PRIVILEGES**
   - Click "Add"

6. **Note down your credentials:**
   ```
   Database Name: yourusername_fagicrm
   Database User: yourusername_fagicrm_user
   Database Password: [your generated password]
   Database Host: localhost
   Database Port: 3306
   ```

---

## Step 2: Setup Python Application in cPanel

1. **Go to cPanel → "Setup Python App"**
2. **Click "Create Application"**
3. **Configure the application:**
   ```
   Python Version: 3.9 or higher (select highest available)
   Application Root: /home/yourusername/fagicrm.fagitone.com
   Application URL: / (or leave blank for root domain)
   Application Startup File: passenger_wsgi.py
   Application Entry Point: application
   ```
4. **Click "Create"**
5. **Note the virtual environment path** shown (e.g., `/home/yourusername/virtualenv/fagicrm.fagitone.com/3.9`)

---

## Step 3: Upload Project Files

### Option A: Using SSH (Recommended)

```bash
# Connect to your server
ssh yourusername@fagicrm.fagitone.com

# Navigate to the application directory
cd ~/fagicrm.fagitone.com

# Upload the ZIP file (use SCP or SFTP)
# Then extract it
unzip fagicrm_deployment.zip

# Or clone from Git if available
# git clone https://github.com/yourusername/fagiassets.git .
# Then copy the fagicrm folder contents to current directory
```

### Option B: Using cPanel File Manager

1. Go to **File Manager** in cPanel
2. Navigate to `/home/yourusername/`
3. Create folder `fagicrm.fagitone.com` if it doesn't exist
4. Upload `fagicrm_deployment.zip`
5. Right-click and select "Extract"
6. Move all files from the extracted folder to `fagicrm.fagitone.com` directory

---

## Step 4: Configure Environment Variables

1. **Navigate to your application directory**
2. **Rename `.env.production` to `.env`**
3. **Edit the `.env` file with your actual credentials:**

```env
# Django Settings
SECRET_KEY=your-very-long-random-secret-key-change-this-now
DEBUG=False
ALLOWED_HOSTS=fagicrm.fagitone.com,www.fagicrm.fagitone.com

# Database Settings
DB_ENGINE=django.db.backends.mysql
DB_NAME=yourusername_fagicrm
DB_USER=yourusername_fagicrm_user
DB_PASSWORD=your_actual_database_password
DB_HOST=localhost
DB_PORT=3306

# Application Settings
DJANGO_SETTINGS_MODULE=fagicrm.settings_production
```

**Important:** 
- Replace `yourusername` with your actual cPanel username
- Replace `your_actual_database_password` with the password you created
- Generate a new SECRET_KEY (use https://djecrety.ir/ or run `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)

---

## Step 5: Update Configuration Files

### Update `.htaccess`

Edit the `.htaccess` file and replace `yourusername` with your actual cPanel username:

```apache
PassengerAppRoot /home/yourusername/fagicrm.fagitone.com
```

### Update `passenger_wsgi.py`

The file should already be configured correctly, but verify it contains:

```python
os.environ['DJANGO_SETTINGS_MODULE'] = 'fagicrm.settings_production'
```

---

## Step 6: Deploy the Application

### Using SSH (Recommended):

```bash
# Navigate to application directory
cd ~/fagicrm.fagitone.com

# Make deployment script executable
chmod +x cpanel_deploy.sh

# Run deployment script
./cpanel_deploy.sh
```

### Manual Deployment:

```bash
# Activate virtual environment
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

---

## Step 7: Create Admin User

```bash
# SSH into your server
cd ~/fagicrm.fagitone.com

# Activate virtual environment
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate

# Create superuser
python manage.py createsuperuser

# Follow the prompts to create your admin account
```

---

## Step 8: Restart Application

1. **Go to cPanel → "Setup Python App"**
2. **Find your application** (fagicrm.fagitone.com)
3. **Click the "Restart" button** (circular arrow icon)
4. **Wait for the application to restart** (usually takes 10-30 seconds)

---

## Step 9: Test Your Deployment

1. **Visit your website:** https://fagicrm.fagitone.com
2. **Test the admin panel:** https://fagicrm.fagitone.com/admin/
3. **Login with your superuser credentials**
4. **Check that static files are loading** (CSS, JavaScript)

---

## Troubleshooting

### Issue: 500 Internal Server Error

**Check error logs:**
```bash
# View Django error log
tail -f ~/fagicrm.fagitone.com/django_errors.log

# View Apache error log
tail -f ~/logs/error_log
```

**Common causes:**
- Incorrect database credentials in `.env`
- Missing dependencies
- Wrong file permissions
- Incorrect `ALLOWED_HOSTS` setting

**Solutions:**
1. Verify `.env` file has correct database credentials
2. Run `pip install -r requirements.txt` again
3. Check file permissions: `chmod -R 755 ~/fagicrm.fagitone.com`
4. Restart the application in cPanel

### Issue: Static Files Not Loading (No CSS)

**Solutions:**
```bash
# Collect static files again
cd ~/fagicrm.fagitone.com
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate
python manage.py collectstatic --noinput --clear

# Set proper permissions
chmod -R 755 staticfiles

# Restart application in cPanel
```

### Issue: Database Connection Error

**Check:**
1. Database name includes your cPanel username prefix
2. Database user has ALL PRIVILEGES
3. Password is correct (no extra spaces)
4. MySQL service is running

**Test database connection:**
```bash
cd ~/fagicrm.fagitone.com
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate
python manage.py dbshell
```

### Issue: Module Not Found

**Solution:**
```bash
# Activate virtual environment
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate

# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Restart application
```

### Issue: Permission Denied

**Solution:**
```bash
cd ~/fagicrm.fagitone.com

# Fix permissions
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;
chmod +x cpanel_deploy.sh
chmod -R 777 media
```

---

## Updating Your Application

When you need to update your application:

```bash
# SSH into server
cd ~/fagicrm.fagitone.com

# Backup database first (optional but recommended)
mysqldump -u yourusername_fagicrm_user -p yourusername_fagicrm > backup_$(date +%Y%m%d).sql

# Pull latest changes (if using Git)
# git pull origin main

# Or upload new files via File Manager/FTP

# Activate virtual environment
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application in cPanel
```

---

## Security Checklist

- [ ] Changed `SECRET_KEY` to a unique random value
- [ ] Set `DEBUG=False` in `.env`
- [ ] Updated `ALLOWED_HOSTS` with your domain
- [ ] Using a strong database password
- [ ] SSL certificate installed (HTTPS enabled)
- [ ] File permissions set correctly (755 for directories, 644 for files)
- [ ] `.env` file is not publicly accessible
- [ ] Regular database backups configured

---

## Important URLs

- **Website:** https://fagicrm.fagitone.com
- **Admin Panel:** https://fagicrm.fagitone.com/admin/
- **Dashboard:** https://fagicrm.fagitone.com/dashboard/

---

## Support & Additional Help

If you encounter issues:

1. Check the error logs (see Troubleshooting section)
2. Verify all configuration files are correct
3. Ensure database credentials are accurate
4. Make sure Python version is 3.8 or higher
5. Contact your hosting provider for cPanel-specific issues

---

## File Structure

```
fagicrm.fagitone.com/
├── .env                    # Environment variables (create from .env.production)
├── .htaccess              # Apache configuration
├── passenger_wsgi.py      # WSGI entry point
├── cpanel_deploy.sh       # Deployment script
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
├── fagicrm/              # Main Django project
│   ├── settings.py       # Base settings
│   ├── settings_production.py  # Production settings
│   ├── urls.py
│   └── wsgi.py
├── customers/            # Customer app
├── employees/            # Employee app
├── services/             # Services app
├── tracking/             # Tracking app
├── dashboard/            # Dashboard app
├── templates/            # HTML templates
├── static/               # Static source files
├── staticfiles/          # Collected static files (generated)
└── media/                # User uploaded files
```

---

## Quick Command Reference

```bash
# Activate virtual environment
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Check for errors
python manage.py check

# View logs
tail -f django_errors.log
tail -f ~/logs/error_log

# Database shell
python manage.py dbshell

# Django shell
python manage.py shell
```

---

**Deployment Date:** $(date)
**Version:** 1.0
**Domain:** fagicrm.fagitone.com