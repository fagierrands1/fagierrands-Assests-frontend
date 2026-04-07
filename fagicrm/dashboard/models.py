from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta


class DashboardWidget(models.Model):
    """Custom dashboard widgets for users"""
    WIDGET_TYPE_CHOICES = [
        ('sales_summary', 'Sales Summary'),
        ('activity_summary', 'Activity Summary'),
        ('task_list', 'Task List'),
        ('recent_customers', 'Recent Customers'),
        ('recent_leads', 'Recent Leads'),
        ('service_requests', 'Service Requests'),
        ('kpi_chart', 'KPI Chart'),
        ('performance_chart', 'Performance Chart'),
        ('calendar', 'Calendar'),
        ('notifications', 'Notifications'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_widgets')
    widget_type = models.CharField(max_length=30, choices=WIDGET_TYPE_CHOICES)
    title = models.CharField(max_length=100)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)
    height = models.IntegerField(default=3)
    is_visible = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
        unique_together = ['user', 'widget_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Notification(models.Model):
    """System notifications for users"""
    NOTIFICATION_TYPE_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
        ('task_due', 'Task Due'),
        ('lead_follow_up', 'Lead Follow-up'),
        ('service_request', 'Service Request'),
        ('kpi_alert', 'KPI Alert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='info')
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    customer_id = models.IntegerField(null=True, blank=True)
    lead_id = models.IntegerField(null=True, blank=True)
    service_request_id = models.IntegerField(null=True, blank=True)
    task_id = models.IntegerField(null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class SystemAlert(models.Model):
    """System-wide alerts and announcements"""
    ALERT_TYPE_CHOICES = [
        ('maintenance', 'Maintenance'),
        ('update', 'System Update'),
        ('announcement', 'Announcement'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Targeting
    target_all_users = models.BooleanField(default=True)
    target_departments = models.ManyToManyField('employees.Department', blank=True)
    target_users = models.ManyToManyField(User, blank=True)
    
    # Scheduling
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_dismissible = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_alerts')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_type.title()} - {self.title}"
    
    @property
    def is_current(self):
        now = timezone.now()
        if self.end_date:
            return self.start_date <= now <= self.end_date
        return self.start_date <= now


class DashboardMetrics:
    """Helper class to calculate dashboard metrics"""
    
    @staticmethod
    def get_sales_summary(user=None, employee=None, days=30):
        """Get sales summary for the last N days"""
        from services.models import ServiceRequest
        from customers.models import Lead
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Filter by employee if provided
        service_filter = {'created_at__gte': start_date}
        lead_filter = {'created_at__gte': start_date}
        
        if employee:
            service_filter['assigned_employee'] = employee
            lead_filter['assigned_employee'] = employee
        
        # Service requests
        service_requests = ServiceRequest.objects.filter(**service_filter)
        total_revenue = sum(sr.total_amount for sr in service_requests.filter(status='completed'))
        completed_requests = service_requests.filter(status='completed').count()
        pending_requests = service_requests.filter(status__in=['pending', 'approved', 'assigned']).count()
        
        # Leads
        leads = Lead.objects.filter(**lead_filter)
        new_leads = leads.count()
        converted_leads = leads.filter(status='won').count()
        conversion_rate = (converted_leads / new_leads * 100) if new_leads > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'completed_requests': completed_requests,
            'pending_requests': pending_requests,
            'new_leads': new_leads,
            'converted_leads': converted_leads,
            'conversion_rate': conversion_rate,
        }
    
    @staticmethod
    def get_activity_summary(user=None, employee=None, days=30):
        """Get activity summary for the last N days"""
        from tracking.models import DailyActivity
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        filter_kwargs = {'date__gte': start_date, 'date__lte': end_date}
        if employee:
            filter_kwargs['employee'] = employee
        
        activities = DailyActivity.objects.filter(**filter_kwargs)
        
        total_calls = sum(activity.calls_made for activity in activities)
        total_emails = sum(activity.emails_sent for activity in activities)
        total_meetings = sum(activity.meetings_held for activity in activities)
        total_tasks = sum(activity.tasks_completed for activity in activities)
        total_hours = sum(activity.total_hours_worked for activity in activities)
        avg_productivity = sum(activity.productivity_score for activity in activities) / len(activities) if activities else 0
        
        return {
            'total_calls': total_calls,
            'total_emails': total_emails,
            'total_meetings': total_meetings,
            'total_tasks': total_tasks,
            'total_hours': total_hours,
            'avg_productivity': avg_productivity,
            'active_days': len(activities),
        }
    
    @staticmethod
    def get_kpi_summary(employee, month=None):
        """Get KPI summary for an employee"""
        from employees.models import EmployeeKPI
        
        if not month:
            month = timezone.now().replace(day=1).date()
        
        try:
            kpi = EmployeeKPI.objects.get(employee=employee, month=month)
            return {
                'overall_score': kpi.overall_score,
                'revenue_generated': kpi.revenue_generated,
                'deals_closed': kpi.deals_closed,
                'conversion_rate': kpi.conversion_rate,
                'customer_satisfaction': kpi.customer_satisfaction_score,
                'sales_target_achievement': kpi.sales_target_achievement,
                'activity_target_achievement': kpi.activity_target_achievement,
            }
        except EmployeeKPI.DoesNotExist:
            return {
                'overall_score': 0,
                'revenue_generated': 0,
                'deals_closed': 0,
                'conversion_rate': 0,
                'customer_satisfaction': 0,
                'sales_target_achievement': 0,
                'activity_target_achievement': 0,
            }
    
    @staticmethod
    def get_upcoming_tasks(user=None, employee=None, days=7):
        """Get upcoming tasks"""
        from tracking.models import Task
        
        end_date = timezone.now() + timedelta(days=days)
        
        filter_kwargs = {
            'due_date__lte': end_date,
            'status__in': ['pending', 'in_progress']
        }
        
        if employee:
            filter_kwargs['assigned_to'] = employee
        
        return Task.objects.filter(**filter_kwargs).order_by('due_date')[:10]
    
    @staticmethod
    def get_recent_customers(days=30, limit=10):
        """Get recently added customers"""
        from customers.models import Customer
        
        start_date = timezone.now() - timedelta(days=days)
        return Customer.objects.filter(created_at__gte=start_date).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_recent_leads(days=30, limit=10):
        """Get recently added leads"""
        from customers.models import Lead
        
        start_date = timezone.now() - timedelta(days=days)
        return Lead.objects.filter(created_at__gte=start_date).order_by('-created_at')[:limit]
