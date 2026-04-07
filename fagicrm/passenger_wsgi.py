"""
WSGI config for cPanel deployment using Passenger.
This file is used by cPanel's Python application hosting.
"""

import os
import sys

# Add your project directory to the sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env file
from pathlib import Path
env_file = Path(project_home) / '.env'
if env_file.exists():
    from decouple import Config, RepositoryEnv
    config = Config(RepositoryEnv(str(env_file)))
    
    # Set environment variables from .env
    for key in ['SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'DB_ENGINE', 'DB_NAME', 
                'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DJANGO_SETTINGS_MODULE']:
        try:
            os.environ.setdefault(key, config(key, default=''))
        except:
            pass

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagicrm.settings_production')
os.environ.setdefault('DEBUG', 'False')

# Import Django's WSGI handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()