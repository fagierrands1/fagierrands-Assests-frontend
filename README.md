# FagiAssets Frontend

Static assets and templates for the Asset Management & CRM System.

## Contents

- `/static/` - CSS, JavaScript, images
- `/staticfiles/` - Collected static files  
- `/templates/` - Django HTML templates (main app)
- `/fagicrm/` - Standalone CRM frontend application

## Structure

```
fagierrands-Assests-frontend/
├── static/          # Main app static files
├── staticfiles/     # Collected static files
├── templates/       # Main app templates
└── fagicrm/         # CRM standalone app
    ├── templates/   # CRM templates
    ├── dashboard/   # Dashboard app
    ├── employees/   # Employee management
    ├── customers/   # Customer management
    ├── services/    # Services app
    └── tracking/    # Time tracking
```

## Note

This is a Django server-side rendered application. The frontend is served by the Django backend.

For production, these files are collected and served by the backend using WhiteNoise.
