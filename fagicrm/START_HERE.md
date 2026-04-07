# 🚀 FagiCRM - cPanel Deployment Package

## Welcome!

This package contains everything you need to deploy FagiCRM to your cPanel hosting at **fagicrm.fagitone.com**.

---

## 📋 Quick Start (5 Steps)

### 1️⃣ Create MySQL Database in cPanel
- Go to cPanel → MySQL Databases
- Create database: `fagicrm`
- Create user: `fagicrm_user` with a strong password
- Add user to database with ALL PRIVILEGES

### 2️⃣ Setup Python App in cPanel
- Go to cPanel → Setup Python App
- Create new application:
  - Python Version: 3.9+
  - App Root: `/home/yourusername/fagicrm.fagitone.com`
  - Startup File: `passenger_wsgi.py`

### 3️⃣ Upload Files
- Extract this ZIP to `/home/yourusername/fagicrm.fagitone.com`
- Or use SSH: `cd ~ && unzip fagicrm_deployment.zip -d fagicrm.fagitone.com`

### 4️⃣ Configure & Deploy
```bash
cd ~/fagicrm.fagitone.com
chmod +x quick_setup.sh
./quick_setup.sh
./cpanel_deploy.sh
python manage.py createsuperuser
```

### 5️⃣ Restart & Test
- Go to cPanel → Setup Python App → Click Restart
- Visit: https://fagicrm.fagitone.com
- Login: https://fagicrm.fagitone.com/admin/

---

## 📁 Package Contents

### 📄 Documentation
- **START_HERE.md** (this file) - Quick start guide
- **CPANEL_DEPLOYMENT.md** - Complete deployment guide
- **DEPLOYMENT_CHECKLIST.txt** - Step-by-step checklist
- **DEPLOYMENT_README.txt** - Quick reference

### ⚙️ Configuration Files
- **.env.production** - Environment variables template
- **.htaccess** - Apache configuration
- **passenger_wsgi.py** - WSGI entry point
- **requirements.txt** - Python dependencies

### 🛠️ Scripts
- **cpanel_deploy.sh** - Automated deployment script
- **quick_setup.sh** - Quick configuration wizard
- **generate_secret_key.py** - SECRET_KEY generator

### 📦 Application Files
- **manage.py** - Django management script
- **fagicrm/** - Main Django project
- **customers/** - Customer management app
- **employees/** - Employee management app
- **services/** - Services app
- **tracking/** - Activity tracking app
- **dashboard/** - Dashboard app
- **templates/** - HTML templates
- **static/** - Static files (CSS, JS, images)

---

## 🎯 Recommended Deployment Method

### Method 1: Using Quick Setup Script (Easiest)

```bash
# 1. SSH into your server
ssh yourusername@fagicrm.fagitone.com

# 2. Navigate to application directory
cd ~/fagicrm.fagitone.com

# 3. Run quick setup wizard
chmod +x quick_setup.sh
./quick_setup.sh

# 4. Deploy application
./cpanel_deploy.sh

# 5. Create admin user
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate
python manage.py createsuperuser

# 6. Restart in cPanel
```

### Method 2: Manual Configuration

1. **Copy .env.production to .env**
   ```bash
   cp .env.production .env
   ```

2. **Edit .env with your credentials**
   ```bash
   nano .env
   ```

3. **Update .htaccess**
   - Replace `yourusername` with your cPanel username

4. **Run deployment**
   ```bash
   chmod +x cpanel_deploy.sh
   ./cpanel_deploy.sh
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

---

## 🔐 Security Checklist

Before going live, ensure:

- [ ] Changed SECRET_KEY to a unique random value
- [ ] Set DEBUG=False in .env
- [ ] Updated ALLOWED_HOSTS with your domain
- [ ] Using a strong database password
- [ ] SSL certificate is installed (HTTPS)
- [ ] File permissions are correct (755/644)
- [ ] .env file is not publicly accessible

---

## 🆘 Troubleshooting

### 500 Internal Server Error
```bash
# Check error logs
tail -f ~/fagicrm.fagitone.com/django_errors.log
tail -f ~/logs/error_log

# Common fixes:
# 1. Check database credentials in .env
# 2. Verify ALLOWED_HOSTS includes your domain
# 3. Run: pip install -r requirements.txt
# 4. Restart application in cPanel
```

### Static Files Not Loading
```bash
# Recollect static files
cd ~/fagicrm.fagitone.com
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate
python manage.py collectstatic --noinput --clear
chmod -R 755 staticfiles

# Restart application in cPanel
```

### Database Connection Error
```bash
# Verify database credentials
# Database name should be: yourusername_fagicrm
# Database user should be: yourusername_fagicrm_user
# Check for typos in .env file

# Test connection
python manage.py dbshell
```

### Module Not Found
```bash
# Reinstall dependencies
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Additional Resources

### Important URLs
- **Website:** https://fagicrm.fagitone.com
- **Admin Panel:** https://fagicrm.fagitone.com/admin/
- **Dashboard:** https://fagicrm.fagitone.com/dashboard/

### Useful Commands
```bash
# Activate virtual environment
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Database shell
python manage.py dbshell

# Check for errors
python manage.py check

# View logs
tail -f django_errors.log
```

### File Permissions
```bash
# Set correct permissions
cd ~/fagicrm.fagitone.com
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;
chmod +x *.sh
chmod -R 777 media
```

---

## 🔄 Updating Your Application

When you need to update:

```bash
# 1. Backup database
mysqldump -u yourusername_fagicrm_user -p yourusername_fagicrm > backup.sql

# 2. Upload new files (or git pull)
cd ~/fagicrm.fagitone.com
# Upload new files here

# 3. Activate virtual environment
source ~/virtualenv/fagicrm.fagitone.com/3.9/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run migrations
python manage.py migrate

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Restart application in cPanel
```

---

## 📞 Support

### Before Contacting Support

1. Check the error logs:
   - `~/fagicrm.fagitone.com/django_errors.log`
   - `~/logs/error_log`

2. Verify your configuration:
   - Database credentials in `.env`
   - `ALLOWED_HOSTS` setting
   - File permissions

3. Try common fixes:
   - Restart application in cPanel
   - Recollect static files
   - Reinstall dependencies

### Getting Help

- **Documentation:** See CPANEL_DEPLOYMENT.md for detailed guide
- **Checklist:** Use DEPLOYMENT_CHECKLIST.txt for step-by-step process
- **Hosting Support:** Contact your cPanel hosting provider
- **Application Issues:** Check Django error logs

---

## ✅ Post-Deployment Checklist

After deployment, verify:

- [ ] Website loads at https://fagicrm.fagitone.com
- [ ] Admin panel accessible at /admin/
- [ ] Can login with superuser account
- [ ] Static files loading (CSS, JavaScript)
- [ ] Dashboard accessible at /dashboard/
- [ ] Can create customers, employees, services
- [ ] No errors in django_errors.log
- [ ] SSL certificate active (HTTPS working)

---

## 🎉 Success!

If everything is working:

1. **Document your credentials** securely
2. **Set up regular backups** (database and media files)
3. **Monitor error logs** regularly
4. **Keep Django and dependencies updated**
5. **Test all features** thoroughly

---

## 📝 Notes

- Default timezone: Africa/Nairobi (EAT, UTC+3)
- Database: MySQL (recommended for cPanel)
- Python version: 3.8+ (3.9+ recommended)
- Django version: 4.2.7

---

**Need more help?** See **CPANEL_DEPLOYMENT.md** for the complete deployment guide with detailed explanations.

**Ready to deploy?** Follow the Quick Start steps above!

---

*Last Updated: 2024*
*Version: 1.0*
*Domain: fagicrm.fagitone.com*