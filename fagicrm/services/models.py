from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Service(models.Model):
    PRICING_TYPE_CHOICES = [
        ('fixed', 'Fixed Price'),
        ('hourly', 'Hourly Rate'),
        ('per_item', 'Per Item'),
        ('custom', 'Custom Quote'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    description = models.TextField()
    
    # Pricing
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPE_CHOICES, default='fixed')
    base_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Service Details
    estimated_duration_minutes = models.IntegerField(default=60, help_text="Estimated time to complete in minutes")
    requires_approval = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category__name', 'name']
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('assigned', 'Assigned'),
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
    
    # Request Information
    request_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='service_requests')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='requests')
    
    # Request Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    special_instructions = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Scheduling
    requested_date = models.DateTimeField()
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Assignment
    assigned_employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests')
    
    # Location
    service_address = models.TextField(help_text="Address where service will be performed")
    
    # Status and Progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress_percentage = models.IntegerField(default=0, help_text="0-100")
    
    # Pricing
    quoted_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    additional_charges = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Customer Feedback
    customer_rating = models.IntegerField(null=True, blank=True, help_text="1-5 stars")
    customer_feedback = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_requests')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['request_id']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['assigned_employee', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['requested_date']),
        ]
    
    def __str__(self):
        return f"{self.request_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.request_id:
            # Generate unique request ID
            import uuid
            self.request_id = f"SR{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate total amount
        from decimal import Decimal
        quoted = Decimal(str(self.quoted_amount)) if self.quoted_amount else Decimal('0')
        additional = Decimal(str(self.additional_charges)) if self.additional_charges else Decimal('0')
        self.total_amount = quoted + additional
        
        # Update completion date when status changes to completed
        if self.status == 'completed' and not self.completed_date:
            self.completed_date = timezone.now()
            self.progress_percentage = 100
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        if self.scheduled_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.scheduled_date
        return False
    
    @property
    def duration_hours(self):
        if self.completed_date and self.scheduled_date:
            duration = self.completed_date - self.scheduled_date
            return duration.total_seconds() / 3600
        return None


class ServiceRequestUpdate(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='updates')
    update_text = models.TextField()
    status_changed_to = models.CharField(max_length=20, blank=True, null=True)
    progress_percentage = models.IntegerField(null=True, blank=True)
    
    # Attachments
    image = models.ImageField(upload_to='service_updates/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update for {self.service_request.request_id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ServiceQuote(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    quote_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE, related_name='quotes')
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='quotes', null=True, blank=True)
    
    # Quote Details
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Validity
    valid_until = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Terms
    terms_and_conditions = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_quotes')
    
    # Response tracking
    sent_date = models.DateTimeField(null=True, blank=True)
    responded_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['quote_id']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['valid_until']),
        ]
    
    def __str__(self):
        return f"{self.quote_id} - {self.customer.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.quote_id:
            # Generate unique quote ID
            import uuid
            self.quote_id = f"QT{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate total
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.valid_until and self.status not in ['accepted', 'rejected']


class ServiceQuoteItem(models.Model):
    quote = models.ForeignKey(ServiceQuote, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1.00)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        ordering = ['id']
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.service.name} - {self.quantity} x ${self.unit_price}"


class ServiceFeedback(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='detailed_feedback')
    
    # Ratings (1-5 scale)
    overall_satisfaction = models.IntegerField(help_text="1-5 stars")
    service_quality = models.IntegerField(help_text="1-5 stars")
    timeliness = models.IntegerField(help_text="1-5 stars")
    communication = models.IntegerField(help_text="1-5 stars")
    value_for_money = models.IntegerField(help_text="1-5 stars")
    
    # Feedback
    positive_feedback = models.TextField(blank=True, null=True)
    improvement_suggestions = models.TextField(blank=True, null=True)
    would_recommend = models.BooleanField(default=True)
    would_use_again = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback for {self.service_request.request_id}"
    
    @property
    def average_rating(self):
        ratings = [
            self.overall_satisfaction,
            self.service_quality,
            self.timeliness,
            self.communication,
            self.value_for_money
        ]
        return sum(ratings) / len(ratings)
