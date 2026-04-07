from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from decimal import Decimal


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Employee(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('terminated', 'Terminated'),
        ('on_leave', 'On Leave'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
    ]
    
    # Link to Django User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    
    # Personal Information
    employee_id = models.CharField(max_length=20, unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(validators=[phone_regex], max_length=17)
    
    # Employment Information
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    position = models.CharField(max_length=100)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    
    # Reporting Structure
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports')
    
    # Compensation
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000, help_text="Commission rate as decimal (e.g., 0.05 for 5%)")
    
    # Performance Targets
    monthly_sales_target = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monthly_calls_target = models.IntegerField(default=0)
    monthly_meetings_target = models.IntegerField(default=0)
    
    # Profile
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='employee_profiles/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['employment_status']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    @property
    def is_manager(self):
        return self.direct_reports.exists() or self.managed_departments.exists()
    
    def get_current_month_performance(self):
        """Get current month performance metrics"""
        from tracking.models import DailyActivity
        from services.models import ServiceRequest
        
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get daily activities for current month
        activities = DailyActivity.objects.filter(
            employee=self,
            date__gte=current_month_start.date(),
            date__lte=now.date()
        )
        
        # Get service requests for current month
        service_requests = ServiceRequest.objects.filter(
            assigned_employee=self,
            created_at__gte=current_month_start
        )
        
        total_calls = sum(activity.calls_made for activity in activities)
        total_emails = sum(activity.emails_sent for activity in activities)
        total_meetings = sum(activity.meetings_held for activity in activities)
        total_revenue = sum(sr.total_amount for sr in service_requests.filter(status='completed'))
        completed_requests = service_requests.filter(status='completed').count()
        
        return {
            'calls_made': total_calls,
            'emails_sent': total_emails,
            'meetings_held': total_meetings,
            'revenue_generated': total_revenue,
            'completed_requests': completed_requests,
            'calls_target_percentage': (total_calls / self.monthly_calls_target * 100) if self.monthly_calls_target > 0 else 0,
            'meetings_target_percentage': (total_meetings / self.monthly_meetings_target * 100) if self.monthly_meetings_target > 0 else 0,
            'sales_target_percentage': (total_revenue / self.monthly_sales_target * 100) if self.monthly_sales_target > 0 else 0,
        }
    
    def get_current_month_performance(self):
        """Get current month performance data"""
        from django.utils import timezone
        current_month = timezone.now().replace(day=1).date()
        
        try:
            kpi = self.performance_kpis.get(month=current_month)
            return {
                'overall_score': float(kpi.overall_score) if kpi.overall_score else 0,
                'revenue_generated': float(kpi.revenue_generated) if kpi.revenue_generated else 0,
                'deals_closed': kpi.deals_closed or 0,
                'conversion_rate': float(kpi.conversion_rate) if kpi.conversion_rate else 0,
                'customer_satisfaction': float(kpi.customer_satisfaction_score) if kpi.customer_satisfaction_score else 0,
                'sales_target_achievement': float(kpi.sales_target_achievement) if kpi.sales_target_achievement else 0,
                'activity_target_achievement': float(kpi.activity_target_achievement) if kpi.activity_target_achievement else 0,
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
    
    @property
    def direct_reports(self):
        """Get employees who report to this employee"""
        return Employee.objects.filter(manager=self)


class EmployeeKPI(models.Model):
    """Monthly KPI tracking for employees"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_kpis')
    month = models.DateField(help_text="First day of the month")
    
    # Sales Metrics
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deals_closed = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Percentage")
    
    # Activity Metrics
    calls_made = models.IntegerField(default=0)
    emails_sent = models.IntegerField(default=0)
    meetings_held = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    
    # Customer Metrics
    new_customers_acquired = models.IntegerField(default=0)
    customer_satisfaction_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, help_text="Out of 5.0")
    customer_retention_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Percentage")
    
    # Productivity Metrics
    average_response_time_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    service_completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Percentage")
    
    # Target Achievement
    sales_target_achievement = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Percentage")
    activity_target_achievement = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Percentage")
    
    # Overall Performance Score
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Calculated overall performance score")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    calculated_at = models.DateTimeField(null=True, blank=True, help_text="When KPIs were last calculated")
    
    class Meta:
        unique_together = ['employee', 'month']
        ordering = ['-month', 'employee__user__first_name']
        indexes = [
            models.Index(fields=['employee', 'month']),
            models.Index(fields=['month']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.month.strftime('%B %Y')}"
    
    def calculate_overall_score(self):
        """Calculate overall performance score based on various metrics"""
        from decimal import Decimal
        
        score = 0
        weight_total = 0
        
        # Sales performance (30% weight)
        if self.sales_target_achievement > 0:
            score += float(min(self.sales_target_achievement, 150)) * 0.3  # Cap at 150%
            weight_total += 0.3
        
        # Activity performance (25% weight)
        if self.activity_target_achievement > 0:
            score += float(min(self.activity_target_achievement, 150)) * 0.25
            weight_total += 0.25
        
        # Customer satisfaction (20% weight)
        if self.customer_satisfaction_score:
            score += (float(self.customer_satisfaction_score) / 5.0 * 100) * 0.2
            weight_total += 0.2
        
        # Service completion rate (15% weight)
        if self.service_completion_rate > 0:
            score += float(min(self.service_completion_rate, 100)) * 0.15
            weight_total += 0.15
        
        # Response time (10% weight) - inverse scoring
        if self.average_response_time_hours > 0:
            # Better (lower) response time gets higher score
            response_score = max(0, 100 - (float(self.average_response_time_hours) * 2))
            score += response_score * 0.1
            weight_total += 0.1
        
        # Normalize score if not all metrics are available
        if weight_total > 0:
            self.overall_score = Decimal(str(score / weight_total))
        else:
            self.overall_score = Decimal('0')
        
        return self.overall_score
    
    def save(self, *args, **kwargs):
        self.calculate_overall_score()
        super().save(*args, **kwargs)


class EmployeeGoal(models.Model):
    GOAL_TYPE_CHOICES = [
        ('sales', 'Sales'),
        ('activity', 'Activity'),
        ('customer_satisfaction', 'Customer Satisfaction'),
        ('productivity', 'Productivity'),
        ('personal_development', 'Personal Development'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_type = models.CharField(max_length=30, choices=GOAL_TYPE_CHOICES)
    
    # Target and Progress
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit = models.CharField(max_length=50, help_text="e.g., 'dollars', 'calls', 'customers', 'hours'")
    
    # Timeline
    start_date = models.DateField()
    target_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_goals')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['target_date']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.title}"
    
    @property
    def progress_percentage(self):
        if self.target_value > 0:
            return min((self.current_value / self.target_value) * 100, 100)
        return 0
    
    @property
    def is_overdue(self):
        return self.target_date < timezone.now().date() and self.status == 'active'
    
    def update_progress(self, new_value):
        """Update progress and check if goal is completed"""
        self.current_value = new_value
        if self.current_value >= self.target_value and self.status == 'active':
            self.status = 'completed'
            self.completed_date = timezone.now().date()
        self.save()
