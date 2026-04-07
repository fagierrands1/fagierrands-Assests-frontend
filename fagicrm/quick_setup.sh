#!/bin/bash

# Quick Setup Script for FagiCRM on cPanel
# This script helps you configure the application quickly

echo "=========================================="
echo "FagiCRM - Quick Setup Wizard"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file already exists!${NC}"
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo -e "${BLUE}This wizard will help you create your .env configuration file.${NC}"
echo ""

# Get cPanel username
echo -e "${YELLOW}Step 1: cPanel Information${NC}"
read -p "Enter your cPanel username: " cpanel_user
echo ""

# Get database information
echo -e "${YELLOW}Step 2: Database Information${NC}"
echo "Note: Your database name will be: ${cpanel_user}_fagicrm"
echo "      Your database user will be: ${cpanel_user}_fagicrm_user"
read -p "Enter your database password: " db_password
echo ""

# Generate SECRET_KEY
echo -e "${YELLOW}Step 3: Generating SECRET_KEY...${NC}"
if command -v python3 &> /dev/null; then
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    echo -e "${GREEN}✓ SECRET_KEY generated${NC}"
else
    SECRET_KEY="CHANGE-THIS-TO-A-RANDOM-SECRET-KEY-$(date +%s)"
    echo -e "${YELLOW}⚠ Python3 not found, using temporary key. Please change it later!${NC}"
fi
echo ""

# Create .env file
echo -e "${YELLOW}Step 4: Creating .env file...${NC}"
cat > .env << EOF
# Django Settings
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=fagicrm.fagitone.com,www.fagicrm.fagitone.com

# Database Settings
DB_ENGINE=django.db.backends.mysql
DB_NAME=${cpanel_user}_fagicrm
DB_USER=${cpanel_user}_fagicrm_user
DB_PASSWORD=${db_password}
DB_HOST=localhost
DB_PORT=3306

# Application Settings
DJANGO_SETTINGS_MODULE=fagicrm.settings_production
EOF

echo -e "${GREEN}✓ .env file created${NC}"
echo ""

# Update .htaccess
echo -e "${YELLOW}Step 5: Updating .htaccess...${NC}"
if [ -f ".htaccess" ]; then
    sed -i "s/yourusername/${cpanel_user}/g" .htaccess
    echo -e "${GREEN}✓ .htaccess updated${NC}"
else
    echo -e "${RED}✗ .htaccess file not found${NC}"
fi
echo ""

# Summary
echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "Configuration Summary:"
echo "----------------------"
echo "cPanel Username: ${cpanel_user}"
echo "Database Name: ${cpanel_user}_fagicrm"
echo "Database User: ${cpanel_user}_fagicrm_user"
echo "Domain: fagicrm.fagitone.com"
echo ""
echo "Next Steps:"
echo "1. Review the .env file and make any necessary changes"
echo "2. Run: chmod +x cpanel_deploy.sh"
echo "3. Run: ./cpanel_deploy.sh"
echo "4. Create superuser: python manage.py createsuperuser"
echo "5. Restart your Python app in cPanel"
echo ""
echo -e "${YELLOW}Important: Make sure you have created the MySQL database in cPanel first!${NC}"
echo ""