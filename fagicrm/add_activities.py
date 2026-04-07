#!/usr/bin/env python
"""
Add sample daily activities and tasks to the CRM system
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fagicrm.settings')
django.setup()

from django.utils import timezone
from employees.models import Employee
from customers.models import Customer, Lead
from tracking.models import DailyActivity, Task
from dashboard.models import Notification

def create_daily_activities():
    """Create sample daily activities for employees"""
    employees = Employee.objects.filter(employment_status='active')[:5]  # First 5 employees
    
    print("Creating daily activities...")
    
    for employee in employees:
        # Create activities for the last 30 days
        for days_ago in range(30):
            date = timezone.now().date() - timedelta(days=days_ago)
            
            # Skip if activity already exists
            if DailyActivity.objects.filter(employee=employee, date=date).exists():
                continue
            
            from datetime import time
            clock_in = time(8, random.randint(0, 30))
            clock_out = time(17, random.randint(0, 30))
            
            DailyActivity.objects.create(
                employee=employee,
                date=date,
                clock_in_time=clock_in,
                clock_out_time=clock_out,
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
    
    print(f"Created daily activities for {employees.count()} employees over 30 days")

def create_tasks():
    """Create sample tasks"""
    employees = Employee.objects.filter(employment_status='active')
    customers = Customer.objects.all()
    leads = Lead.objects.all()
    
    print("Creating tasks...")
    
    task_titles = [
        "Follow up with customer inquiry",
        "Prepare service quote",
        "Schedule customer meeting",
        "Complete service delivery",
        "Update customer records",
        "Process payment",
        "Conduct customer satisfaction survey",
        "Prepare monthly report",
        "Review service requests",
        "Update lead status"
    ]
    
    task_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    priorities = ['low', 'medium', 'high']
    
    for i in range(50):
        assigned_to = random.choice(employees)
        assigned_by = random.choice(employees).user
        
        Task.objects.create(
            title=random.choice(task_titles),
            description=f'Description for task {i+1}',
            assigned_to=assigned_to,
            assigned_by=assigned_by,
            status=random.choice(task_statuses),
            priority=random.choice(priorities),
            due_date=timezone.now() + timedelta(days=random.randint(-5, 30)),
            progress_percentage=random.randint(0, 100),
            estimated_hours=random.randint(1, 8),
            actual_hours=random.randint(1, 10) if random.choice([True, False]) else None,
            customer=random.choice(customers) if customers.exists() and random.choice([True, False]) else None,
            lead=random.choice(leads) if leads.exists() and random.choice([True, False]) else None,
            notes=f'Sample notes for task {i+1}'
        )
    
    print("Created 50 tasks")

def create_notifications():
    """Create sample notifications"""
    employees = Employee.objects.filter(employment_status='active')
    
    print("Creating notifications...")
    
    notification_types = ['info', 'warning', 'success', 'task_due', 'lead_follow_up']
    
    notification_templates = {
        'info': [
            ('System Update', 'The CRM system has been updated with new features.'),
            ('New Feature Available', 'Check out the new dashboard analytics feature.'),
            ('Maintenance Notice', 'Scheduled maintenance will occur this weekend.'),
        ],
        'warning': [
            ('Target Alert', 'You are behind on your monthly sales target.'),
            ('Overdue Tasks', 'You have overdue tasks that need attention.'),
            ('Customer Follow-up', 'Several customers need follow-up calls.'),
        ],
        'success': [
            ('Target Achieved', 'Congratulations! You have achieved your monthly target.'),
            ('Deal Closed', 'Great job closing the deal with ABC Company.'),
            ('Customer Satisfaction', 'You received excellent customer feedback.'),
        ],
        'task_due': [
            ('Task Due Soon', 'You have a task due tomorrow.'),
            ('Overdue Task', 'A task assigned to you is now overdue.'),
            ('Task Reminder', 'Reminder: Complete your assigned tasks.'),
        ],
        'lead_follow_up': [
            ('Lead Follow-up Required', 'A lead needs immediate follow-up.'),
            ('Hot Lead Alert', 'You have a hot lead that needs attention.'),
            ('Lead Status Update', 'Please update the status of your leads.'),
        ]
    }
    
    for employee in employees:
        for i in range(random.randint(3, 8)):
            notification_type = random.choice(notification_types)
            title, message = random.choice(notification_templates[notification_type])
            
            Notification.objects.create(
                user=employee.user,
                notification_type=notification_type,
                title=title,
                message=message,
                is_read=random.choice([True, False])
            )
    
    print(f"Created notifications for {employees.count()} employees")

if __name__ == '__main__':
    print("🔧 Adding sample activities and tasks to FAGI CRM...")
    
    create_daily_activities()
    create_tasks()
    create_notifications()
    
    print("\n✅ Sample data added successfully!")
    print("📊 Updated Statistics:")
    print(f"   • Daily Activities: {DailyActivity.objects.count()}")
    print(f"   • Tasks: {Task.objects.count()}")
    print(f"   • Notifications: {Notification.objects.count()}")