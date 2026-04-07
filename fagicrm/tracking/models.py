from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class DailyActivity(models.Model):
    """Track daily activities for each employee"""
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='daily_activities')
    date = models.DateField()
    
    # Time Tracking
    clock_in_time = models.TimeField(null=True, blank=True)
    clock_out_time = models.TimeField(null=True, blank=True)
    break_duration_minutes = models.IntegerField(default=0)
    total_hours_worked = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    
    # Sales Activities
    calls_made = models.IntegerField(default=0)
    emails_sent = models.IntegerField(default=0)
    meetings_held = models.IntegerField(default=0)
    leads_contacted = models.IntegerField(default=0)
    demos_given = models.IntegerField(default=0)
    deals_closed = models.IntegerField(default=0)
    
    # Customer Interactions
    customer_calls = models.IntegerField(default=0)
    customer_emails = models.IntegerField(default=0)
    customer_meetings = models.IntegerField(default=0)
    follow_ups_completed = models.IntegerField(default=0)
    
    # Task Management
    tasks_assigned = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    tasks_overdue = models.IntegerField(default=0)
    
    # Service Requests
    service_requests_handled = models.IntegerField(default=0)
    service_requests_completed = models.IntegerField(default=0)
    
    # Revenue
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Notes
    daily_notes = models.TextField(blank=True, null=True, help_text="Daily summary or notes")
    challenges_faced = models.TextField(blank=True, null=True)
    achievements = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee__user__first_name']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"
    
    def calculate_total_hours(self):
        """Calculate total hours worked based on clock in/out times"""
        if self.clock_in_time and self.clock_out_time:
            # Convert times to datetime for calculation
            today = timezone.now().date()
            clock_in = timezone.datetime.combine(today, self.clock_in_time)
            clock_out = timezone.datetime.combine(today, self.clock_out_time)
            
            # Handle overnight shifts
            if clock_out < clock_in:
                clock_out += timezone.timedelta(days=1)
            
            # Calculate total time minus breaks
            total_minutes = (clock_out - clock_in).total_seconds() / 60
            total_minutes -= self.break_duration_minutes
            
            self.total_hours_worked = Decimal(str(max(0, total_minutes / 60)))
        
        return self.total_hours_worked
    
    def save(self, *args, **kwargs):
        self.calculate_total_hours()
        super().save(*args, **kwargs)
    
    @property
    def productivity_score(self):
        """Calculate a productivity score based on various metrics"""
        score = 0
        
        # Activity score (40% weight)
        activity_score = (self.calls_made * 2 + self.emails_sent * 1 + 
                         self.meetings_held * 5 + self.tasks_completed * 3)
        score += min(activity_score, 100) * 0.4
        
        # Customer interaction score (30% weight)
        customer_score = (self.customer_calls * 3 + self.customer_emails * 2 + 
                         self.customer_meetings * 8 + self.follow_ups_completed * 4)
        score += min(customer_score, 100) * 0.3
        
        # Revenue score (30% weight)
        if self.revenue_generated > 0:
            # Normalize revenue to 0-100 scale (assuming $1000 = 100 points)
            revenue_score = min(float(self.revenue_generated) / 10, 100)
            score += revenue_score * 0.3
        
        return min(score, 100)


class TimeEntry(models.Model):
    """Detailed time tracking for specific activities or projects"""
    ACTIVITY_TYPE_CHOICES = [
        ('customer_call', 'Customer Call'),
        ('lead_call', 'Lead Call'),
        ('meeting', 'Meeting'),
        ('email', 'Email Communication'),
        ('service_delivery', 'Service Delivery'),
        ('admin', 'Administrative Work'),
        ('training', 'Training'),
        ('travel', 'Travel'),
        ('break', 'Break'),
        ('other', 'Other'),
    ]
    
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='time_entries')
    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Activity Details
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPE_CHOICES)
    description = models.TextField()
    
    # Related Objects
    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    lead = models.ForeignKey('customers.Lead', on_delete=models.SET_NULL, null=True, blank=True)
    service_request = models.ForeignKey('services.ServiceRequest', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Time Calculation
    duration_minutes = models.IntegerField(default=0)
    is_billable = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['start_time']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.activity_type} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def calculate_duration(self):
        """Calculate duration in minutes"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)
        return self.duration_minutes
    
    def save(self, *args, **kwargs):
        self.calculate_duration()
        super().save(*args, **kwargs)


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('on_hold', 'On Hold'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Task Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    
    # Related Objects
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    lead = models.ForeignKey('customers.Lead', on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    service_request = models.ForeignKey('services.ServiceRequest', on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    
    # Task Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Timeline
    due_date = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Progress
    progress_percentage = models.IntegerField(default=0, help_text="0-100")
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    completion_notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.full_name}"
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now() and self.status not in ['completed', 'cancelled']
    
    @property
    def days_until_due(self):
        if self.due_date:
            delta = self.due_date.date() - timezone.now().date()
            return delta.days
        return None
    
    def mark_completed(self, completion_notes=None):
        """Mark task as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress_percentage = 100
        if completion_notes:
            self.completion_notes = completion_notes
        self.save()


class PerformanceMetric(models.Model):
    """Store calculated performance metrics for employees"""
    METRIC_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='performance_metrics')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Sales Metrics
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deals_closed = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    average_deal_size = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Activity Metrics
    total_calls = models.IntegerField(default=0)
    total_emails = models.IntegerField(default=0)
    total_meetings = models.IntegerField(default=0)
    total_tasks_completed = models.IntegerField(default=0)
    
    # Time Metrics
    total_hours_worked = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    billable_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    average_response_time_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    # Customer Metrics
    new_customers_acquired = models.IntegerField(default=0)
    customer_satisfaction_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    service_requests_completed = models.IntegerField(default=0)
    
    # Performance Scores
    productivity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    overall_performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Target Achievement
    sales_target_achievement = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    activity_target_achievement = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['employee', 'metric_type', 'period_start', 'period_end']
        ordering = ['-period_start', 'employee__user__first_name']
        indexes = [
            models.Index(fields=['employee', 'metric_type']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.metric_type} - {self.period_start} to {self.period_end}"


class ActivityLog(models.Model):
    """Log all important activities for audit trail"""
    ACTION_TYPE_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('status_change', 'Status Change'),
        ('assignment', 'Assignment'),
        ('completion', 'Completion'),
        ('communication', 'Communication'),
    ]
    
    # Who and When
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # What
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    description = models.TextField()
    
    # Related Objects (using generic foreign key would be better, but keeping simple)
    customer_id = models.IntegerField(null=True, blank=True)
    lead_id = models.IntegerField(null=True, blank=True)
    service_request_id = models.IntegerField(null=True, blank=True)
    task_id = models.IntegerField(null=True, blank=True)
    
    # Additional Data
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['employee', 'timestamp']),
            models.Index(fields=['action_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
