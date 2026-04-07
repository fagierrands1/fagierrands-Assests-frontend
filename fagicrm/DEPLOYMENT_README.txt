================================================================================
                    FagiCRM - cPanel Deployment Package
                         Domain: fagicrm.fagitone.com
================================================================================

QUICK START:
1. Extract this ZIP file to your cPanel application directory
2. Create MySQL database in cPanel
3. Configure .env file with your database credentials
4. Run: ./cpanel_deploy.sh
5. Restart Python app in cPanel
6. Visit: https://fagicrm.fagitone.com

DETAILED INSTRUCTIONS:
See CPANEL_DEPLOYMENT.md for complete step-by-step guide

IMPORTANT FILES:
- CPANEL_DEPLOYMENT.md  : Complete deployment guide
- .env.production       : Template for environment variables (rename to .env)
- passenger_wsgi.py     : WSGI entry point for cPanel
- .htaccess            : Apache configuration
- cpanel_deploy.sh     : Automated deployment script
- requirements.txt     : Python dependencies

BEFORE YOU START:
1. Have your cPanel login credentials ready
2. Create a MySQL database in cPanel
3. Note down database name, user, and password
4. Ensure Python 3.8+ is available in cPanel

FIRST TIME SETUP:
1. Upload and extract this ZIP to: /home/yourusername/fagicrm.fagitone.com
2. Rename .env.production to .env
3. Edit .env with your database credentials
4. Update .htaccess with your username
5. Run: chmod +x cpanel_deploy.sh && ./cpanel_deploy.sh
6. Create admin user: python manage.py createsuperuser
7. Restart app in cPanel → Setup Python App

SUPPORT:
- Check django_errors.log for application errors
- Check ~/logs/error_log for Apache errors
- See CPANEL_DEPLOYMENT.md troubleshooting section

================================================================================