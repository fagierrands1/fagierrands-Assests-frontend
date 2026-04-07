# FAGI CRM - Errand Hailing Service Management System

A comprehensive Customer Relationship Management (CRM) system built with Django for managing errand and service businesses.

## Features

### Core CRM Features
- **Customer Management**: Complete customer profiles with contact information, service history, and notes
- **Lead Management**: Lead tracking from initial contact to conversion
- **Service Request Management**: Handle service requests with status tracking and employee assignment
- **Quote Management**: Generate and manage service quotes
- **Service Catalog**: Manage services and categories with pricing

### Employee Management & Tracking
- **Employee Profiles**: Complete employee information with departments and roles
- **Daily Activity Tracking**: Track daily activities, hours worked, calls made, meetings held
- **Time Entry System**: Detailed time tracking for billable and non-billable activities
- **Task Management**: Assign and track tasks with progress monitoring

### KPI & Performance Management
- **Individual KPIs**: Comprehensive performance metrics for each employee
- **Team Performance**: Manager dashboard for team oversight
- **Performance Metrics**: Revenue, conversion rates, customer satisfaction, target achievement
- **Historical Tracking**: 6-month performance trends and comparisons

### Dashboard & Reporting
- **Interactive Dashboard**: Real-time metrics and key performance indicators
- **Notification System**: Alerts for tasks, follow-ups, and system updates
- **Team Management**: Manager tools for team performance monitoring
- **API Endpoints**: RESTful APIs for data integration

## Technology Stack

- **Backend**: Django 4.2.1
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: Bootstrap 5.3, Chart.js for visualizations
- **Authentication**: Django's built-in authentication system
- **Admin Interface**: Enhanced Django Admin with custom configurations

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fagicrm
   ```

2. **Install dependencies**:
   ```bash
   pip install django django-extensions
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

5. **Create sample data** (optional):
   ```bash
   python manage.py create_sample_data
   ```

6. **Start development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - Main Dashboard: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Default Login Credentials

- **Username**: admin
- **Password**: admin123

## Application Structure

### Apps Overview

1. **employees**: Employee management, KPIs, and performance tracking
2. **customers**: Customer and lead management
3. **services**: Service catalog, requests, and quotes
4. **tracking**: Daily activities, time entries, and task management
5. **dashboard**: Main dashboard, notifications, and reporting

### Key Models

#### Employee Management
- `Employee`: Employee profiles with department and role information
- `EmployeeKPI`: Monthly KPI calculations and performance metrics
- `EmployeeGoal`: Individual and team goals setting
- `Department`: Organizational structure management

#### Customer Management
- `Customer`: Customer profiles and contact information
- `Lead`: Lead tracking and conversion management
- `CustomerNote` / `LeadNote`: Communication history

#### Service Management
- `Service`: Service catalog with pricing and categories
- `ServiceRequest`: Service request lifecycle management
- `ServiceQuote`: Quote generation and approval workflow
- `ServiceFeedback`: Customer feedback collection

#### Activity Tracking
- `DailyActivity`: Daily work activity logging
- `TimeEntry`: Detailed time tracking entries
- `Task`: Task assignment and progress tracking
- `PerformanceMetric`: Performance calculations and analytics

## Key Features Explained

### Daily Activity Tracking
Employees can log their daily activities including:
- Clock in/out times and break duration
- Calls made, emails sent, meetings held
- Customer interactions and follow-ups
- Tasks completed and service requests handled
- Revenue generated and achievements

### KPI Calculation
The system automatically calculates comprehensive KPIs:
- **Revenue Metrics**: Total revenue, deals closed, average deal size
- **Activity Metrics**: Calls, emails, meetings, tasks completed
- **Performance Scores**: Productivity, quality, overall performance
- **Target Achievement**: Sales and activity target percentages
- **Customer Metrics**: Satisfaction, retention, new acquisitions

### Dashboard Features
- **Real-time Metrics**: Live updates of key performance indicators
- **Interactive Charts**: Visual representation of performance data
- **Notification System**: Alerts for important events and deadlines
- **Team Management**: Manager tools for team oversight
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

## Management Commands

### Calculate KPIs
```bash
# Calculate KPIs for current month
python manage.py calculate_kpis

# Calculate for specific month
python manage.py calculate_kpis --month 2024-01

# Calculate for specific employee
python manage.py calculate_kpis --employee-id 1

# Force recalculation
python manage.py calculate_kpis --force
```

### Create Sample Data
```bash
# Create sample data with default counts
python manage.py create_sample_data

# Create custom amounts
python manage.py create_sample_data --employees 20 --customers 100 --leads 50
```

## API Endpoints

### Dashboard APIs
- `GET /dashboard/api/metrics/`: Dashboard metrics
- `GET /dashboard/api/notifications/`: User notifications
- `GET /dashboard/api/employee/{id}/performance/`: Employee performance data
- `GET /dashboard/api/team/performance/`: Team performance data
- `POST /dashboard/api/notifications/create/`: Create notifications

## Customization

### Adding New Service Types
1. Create new `ServiceCategory` in admin
2. Add `Service` entries with appropriate pricing
3. Configure service-specific fields if needed

### Custom KPI Calculations
Modify the `calculate_kpis.py` management command to add custom metrics or adjust calculation formulas.

### Dashboard Widgets
The dashboard supports customizable widgets. Add new widget types in `dashboard/models.py` and corresponding templates.

## Production Deployment

### Environment Variables
Create a `.env` file with:
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost/dbname
ALLOWED_HOSTS=yourdomain.com
```

### Database Configuration
Update `settings.py` for production database:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fagicrm',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Static Files
```bash
python manage.py collectstatic
```

## Support & Maintenance

### Regular Tasks
1. **Daily**: Monitor system performance and user activity
2. **Weekly**: Review KPI calculations and data accuracy
3. **Monthly**: Generate performance reports and backup data
4. **Quarterly**: Review and update service catalog and pricing

### Backup Strategy
- Database backups: Daily automated backups
- File backups: Weekly backup of uploaded files
- Configuration backups: Version control for settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is proprietary software developed for FAGI CRM.

## Contact

For support or questions, contact the development team.