#!/bin/bash

# cPanel Deployment Script for FagiCRM
# This script automates the deployment process on cPanel

echo "=========================================="
echo "FagiCRM - cPanel Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}Step 1: Checking environment...${NC}"
if [ ! -f ".env.production" ]; then
    echo -e "${RED}Error: .env.production file not found!${NC}"
    echo "Please create .env.production file with your database credentials."
    exit 1
fi
echo -e "${GREEN}✓ Environment file found${NC}"
echo ""

echo -e "${YELLOW}Step 2: Activating virtual environment...${NC}"
# Try to find and activate virtual environment
if [ -d "$HOME/virtualenv/fagicrm.fagitone.com" ]; then
    source "$HOME/virtualenv/fagicrm.fagitone.com/*/bin/activate"
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
elif [ -d "$HOME/virtualenv" ]; then
    # Find the first Python virtual environment
    VENV_PATH=$(find "$HOME/virtualenv" -name "activate" | head -1)
    if [ -n "$VENV_PATH" ]; then
        source "$VENV_PATH"
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo -e "${YELLOW}⚠ Virtual environment not found, using system Python${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Virtual environment not found, using system Python${NC}"
fi
echo ""

echo -e "${YELLOW}Step 3: Installing dependencies...${NC}"
pip install -r requirements.txt --upgrade
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 4: Running database migrations...${NC}"
python manage.py migrate --noinput
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations completed${NC}"
else
    echo -e "${RED}✗ Migration failed${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 5: Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Static files collected${NC}"
else
    echo -e "${RED}✗ Failed to collect static files${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 6: Setting file permissions...${NC}"
# Set proper permissions
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;
chmod +x cpanel_deploy.sh
chmod -R 777 media 2>/dev/null || mkdir -p media && chmod -R 777 media
chmod -R 755 staticfiles
echo -e "${GREEN}✓ Permissions set${NC}"
echo ""

echo -e "${GREEN}=========================================="
echo "Deployment completed successfully!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Go to cPanel → Setup Python App"
echo "2. Click 'Restart' on your application"
echo "3. Visit https://fagicrm.fagitone.com"
echo ""
echo "To create a superuser, run:"
echo "  python manage.py createsuperuser"
echo ""