from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

from employees.models import Department, Employee, EmployeeKPI, EmployeeGoal
from customers.models import Customer, Lead, CustomerNote, LeadNote
from services.models import ServiceCategory, Service, ServiceRequest, ServiceQuote
from tracking.models import DailyActivity, TimeEntry, Task, PerformanceMetric
from dashboard.models import Notification


class Command(BaseCommand):
    help = 'Create sample data for the CRM system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--employees',
            type=int,
            default=10,
            help='Number of employees to create',
        )
        parser.add_argument(
            '--customers',
            type=int,
            default=50,
            help='Number of customers to create',
        )
        parser.add_argument(
            '--leads',
            type=int,
            default=30,
            help='Number of leads to create',
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create departments
        departments_data = [
            {'name': 'Sales', 'description': 'Sales and customer acquisition'},
            {'name': 'Customer Service', 'description': 'Customer support and service'},
            {'name': 'Operations', 'description': 'Service delivery and operations'},
            {'name': 'Management', 'description': 'Management and administration'},
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            departments[dept_data['name']] = dept
            if created:
                self.stdout.write(f'Created department: {dept.name}')

        # Create service categories and services
        categories_data = [
            {'name': 'Delivery Services', 'description': 'Package and document delivery'},
            {'name': 'Personal Errands', 'description': 'Personal shopping and errands'},
            {'name': 'Business Services', 'description': 'Business-related errands'},
            {'name': 'Home Services', 'description': 'Home maintenance and services'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = ServiceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(f'Created service category: {cat.name}')

        # Create services
        services_data = [
            {'name': 'Document Delivery', 'category': 'Delivery Services', 'base_price': 15.00},
            {'name': 'Package Pickup & Delivery', 'category': 'Delivery Services', 'base_price': 25.00},
            {'name': 'Grocery Shopping', 'category': 'Personal Errands', 'base_price': 30.00},
            {'name': 'Pharmacy Pickup', 'category': 'Personal Errands', 'base_price': 20.00},
            {'name': 'Bank Errands', 'category': 'Business Services', 'base_price': 25.00},
            {'name': 'Office Supply Pickup', 'category': 'Business Services', 'base_price': 20.00},
            {'name': 'Home Cleaning', 'category': 'Home Services', 'base_price': 80.00},
            {'name': 'Pet Care', 'category': 'Personal Errands', 'base_price': 35.00},
        ]
        
        services = {}
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'category': categories[service_data['category']],
                    'base_price': service_data['base_price'],
                    'pricing_type': 'fixed',
                    'estimated_duration_minutes': random.randint(30, 180),
                }
            )
            services[service_data['name']] = service
            if created:
                self.stdout.write(f'Created service: {service.name}')

        # Create users and employees
        positions = ['Sales Representative', 'Customer Service Rep', 'Operations Manager', 
                    'Service Coordinator', 'Team Lead', 'Account Manager']
        
        employees = []
        for i in range(options['employees']):
            username = f'employee{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@fagicrm.com',
                    password='password123',
                    first_name=f'Employee{i+1}',
                    last_name='User'
                )
                
                dept = random.choice(list(departments.values()))
                employee = Employee.objects.create(
                    user=user,
                    employee_id=f'EMP{1000+i}',
                    position=random.choice(positions),
                    department=dept,
                    employment_status='active',
                    employment_type='full_time',
                    hire_date=timezone.now().date() - timedelta(days=random.randint(30, 1000)),
                    salary=random.randint(40000, 80000),
                    monthly_sales_target=random.randint(5000, 15000),
                    monthly_calls_target=random.randint(50, 150),
                    monthly_meetings_target=random.randint(10, 30),
                    phone=f'+1-555-{random.randint(1000, 9999)}'
                )
                employees.append(employee)
                self.stdout.write(f'Created employee: {employee.full_name}')

        # Assign managers
        for dept in departments.values():
            dept_employees = Employee.objects.filter(department=dept)
            if dept_employees.exists():
                manager = random.choice(dept_employees)
                dept.manager = manager
                dept.save()
                
                # Set some employees as managers by assigning them direct reports
                if dept_employees.count() > 3:
                    manager_employees = random.sample(list(dept_employees), min(2, dept_employees.count()//3))
                    for emp in manager_employees:
                        # Assign some other employees as direct reports
                        potential_reports = dept_employees.exclude(id=emp.id)
                        if potential_reports.exists():
                            reports = random.sample(list(potential_reports), min(2, potential_reports.count()))
                            for report in reports:
                                report.manager = emp
                                report.save()

        # Create customers
        customer_types = ['individual', 'business']
        statuses = ['active', 'inactive', 'potential']
        
        customers = []
        for i in range(options['customers']):
            customer, created = Customer.objects.get_or_create(
                email=f'customer{i+1}@example.com',
                defaults={
                    'first_name': f'Customer{i+1}',
                    'last_name': 'User',
                    'phone': f'+1-555-{random.randint(1000, 9999)}',
                    'customer_type': random.choice(customer_types),
                    'status': random.choice(statuses),
                    'assigned_employee': random.choice(employees) if employees else None,
                    'total_spent': random.randint(0, 5000),
                    'lifetime_value': random.randint(100, 10000),
                    'address_line1': f'{random.randint(100, 9999)} Main St',
                    'city': 'Sample City',
                    'state': 'CA',
                    'postal_code': f'{random.randint(10000, 99999)}',
                    'country': 'USA',
                    'created_by': User.objects.get(username='admin')
                }
            )
            
            if customer.customer_type == 'business':
                customer.company_name = f'Company {i+1} Inc.'
                customer.save()
            
            customers.append(customer)
            
            # Create some customer notes
            if random.choice([True, False]):
                CustomerNote.objects.create(
                    customer=customer,
                    note=f'Sample note for {customer.full_name}',
                    is_important=random.choice([True, False]),
                    created_by=random.choice(employees).user if employees else User.objects.get(username='admin')
                )
        
        self.stdout.write(f'Created {len(customers)} customers')

        # Create leads
        lead_sources = ['website', 'referral', 'social_media', 'advertising', 'cold_call']
        lead_statuses = ['new', 'contacted', 'qualified', 'proposal', 'won', 'lost']
        
        leads = []
        for i in range(options['leads']):
            lead, created = Lead.objects.get_or_create(
                email=f'lead{i+1}@example.com',
                defaults={
                    'first_name': f'Lead{i+1}',
                    'last_name': 'Prospect',
                    'phone': f'+1-555-{random.randint(1000, 9999)}',
                    'status': random.choice(lead_statuses),
                    'source': random.choice(lead_sources),
                    'assigned_employee': random.choice(employees) if employees else None,
                    'estimated_value': random.randint(100, 2000),
                    'interested_services': random.choice(list(services.keys())),
                    'urgency': random.choice(['low', 'medium', 'high']),
                    'notes': f'Sample lead notes for Lead{i+1}',
                    'created_by': User.objects.get(username='admin')
                }
            )
            leads.append(lead)
        
        self.stdout.write(f'Created {len(leads)} leads')

        # Create service requests
        request_statuses = ['pending', 'approved', 'assigned', 'in_progress', 'completed', 'cancelled']
        priorities = ['low', 'medium', 'high', 'urgent']
        
        for i in range(20):
            customer = random.choice(customers)
            service = random.choice(list(services.values()))
            
            ServiceRequest.objects.create(
                customer=customer,
                service=service,
                title=f'Service request for {service.name}',
                description=f'Sample service request description {i+1}',
                status=random.choice(request_statuses),
                priority=random.choice(priorities),
                assigned_employee=random.choice(employees) if employees else None,
                requested_date=timezone.now() + timedelta(days=random.randint(1, 30)),
                quoted_amount=service.base_price + random.randint(-10, 50),
                created_by=User.objects.get(username='admin')
            )
        
        self.stdout.write('Created 20 service requests')

        # Create daily activities for employees
        if employees:
            for employee in employees[:5]:  # Create activities for first 5 employees
                for days_ago in range(30):
                    date = timezone.now().date() - timedelta(days=days_ago)
                    
                    DailyActivity.objects.create(
                        employee=employee,
                        date=date,
                        clock_in_time=timezone.now().replace(hour=8, minute=random.randint(0, 30)),
                        clock_out_time=timezone.now().replace(hour=17, minute=random.randint(0, 30)),
                        break_duration_minutes=random.randint(30, 60),
                        calls_made=random.randint(5, 25),
                        emails_sent=random.randint(10, 40),
                        meetings_held=random.randint(1, 5),
                        leads_contacted=random.randint(2, 10),
                        demos_given=random.randint(0, 3),
                        deals_closed=random.randint(0, 2),
                        customer_calls=random.randint(3, 15),
                        customer_emails=random.randint(5, 20),
                        customer_meetings=random.randint(1, 4),
                        follow_ups_completed=random.randint(2, 8),
                        tasks_assigned=random.randint(3, 10),
                        tasks_completed=random.randint(2, 8),
                        tasks_overdue=random.randint(0, 2),
                        service_requests_handled=random.randint(1, 5),
                        service_requests_completed=random.randint(1, 4),
                        revenue_generated=random.randint(100, 1000),
                        daily_notes=f'Daily notes for {date}',
                        achievements=f'Sample achievements for {date}' if random.choice([True, False]) else '',
                        challenges_faced=f'Sample challenges for {date}' if random.choice([True, False]) else ''
                    )
            
            self.stdout.write('Created daily activities for employees')

            # Create KPIs for employees
            current_month = timezone.now().replace(day=1).date()
            for employee in employees[:5]:
                EmployeeKPI.objects.create(
                    employee=employee,
                    month=current_month,
                    revenue_generated=random.randint(2000, 8000),
                    deals_closed=random.randint(5, 20),
                    conversion_rate=random.randint(10, 40),
                    calls_made=random.randint(100, 300),
                    emails_sent=random.randint(150, 400),
                    meetings_held=random.randint(20, 60),
                    tasks_completed=random.randint(50, 150),
                    new_customers_acquired=random.randint(3, 15),
                    customer_satisfaction_score=random.uniform(3.5, 5.0),
                    customer_retention_rate=random.randint(80, 95),
                    average_response_time_hours=random.uniform(1.0, 8.0),
                    service_completion_rate=random.randint(85, 100),
                    sales_target_achievement=random.randint(70, 120),
                    activity_target_achievement=random.randint(80, 110)
                )
            
            self.stdout.write('Created KPIs for employees')

            # Create some tasks
            task_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
            priorities = ['low', 'medium', 'high']
            
            for i in range(30):
                Task.objects.create(
                    title=f'Sample Task {i+1}',
                    description=f'Description for sample task {i+1}',
                    assigned_to=random.choice(employees),
                    assigned_by=random.choice(employees),
                    status=random.choice(task_statuses),
                    priority=random.choice(priorities),
                    due_date=timezone.now() + timedelta(days=random.randint(-5, 30)),
                    progress_percentage=random.randint(0, 100),
                    estimated_hours=random.randint(1, 8),
                    actual_hours=random.randint(1, 10) if random.choice([True, False]) else None,
                    customer=random.choice(customers) if random.choice([True, False]) else None,
                    lead=random.choice(leads) if random.choice([True, False]) else None,
                    notes=f'Sample notes for task {i+1}'
                )
            
            self.stdout.write('Created 30 tasks')

            # Create notifications
            notification_types = ['info', 'warning', 'success', 'task_due', 'lead_follow_up']
            
            for employee in employees[:5]:
                for i in range(5):
                    Notification.objects.create(
                        user=employee.user,
                        notification_type=random.choice(notification_types),
                        title=f'Sample Notification {i+1}',
                        message=f'This is a sample notification message for {employee.full_name}',
                        is_read=random.choice([True, False])
                    )
            
            self.stdout.write('Created notifications')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(departments)} departments\n'
                f'- {len(employees)} employees\n'
                f'- {len(customers)} customers\n'
                f'- {len(leads)} leads\n'
                f'- Service categories and services\n'
                f'- Service requests, tasks, and activities\n'
                f'- KPIs and notifications'
            )
        )