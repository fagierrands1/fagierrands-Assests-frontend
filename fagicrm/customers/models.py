from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone


class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('business', 'Business'),
        ('corporate', 'Corporate'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='individual')
    
    # Contact Information
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17)
    alternate_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    
    # Address Information
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='USA')
    
    # Business Information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    assigned_employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_customers')
    
    # Preferences
    preferred_contact_method = models.CharField(max_length=20, choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
    ], default='email')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_customers')
    
    # Customer Value
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_employee']),
        ]
    
    def __str__(self):
        if self.company_name:
            return f"{self.company_name} ({self.first_name} {self.last_name})"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        address_parts = [self.address_line1]
        if self.address_line2:
            address_parts.append(self.address_line2)
        address_parts.extend([self.city, self.state, self.postal_code])
        return ", ".join(address_parts)


class Lead(models.Model):
    LEAD_STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal Sent'),
        ('negotiation', 'In Negotiation'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    ]
    
    LEAD_SOURCE_CHOICES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('advertisement', 'Advertisement'),
        ('cold_call', 'Cold Call'),
        ('email_campaign', 'Email Campaign'),
        ('trade_show', 'Trade Show'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    
    # Contact Information
    email = models.EmailField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    
    # Lead Information
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new')
    source = models.CharField(max_length=20, choices=LEAD_SOURCE_CHOICES, default='website')
    assigned_employee = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
    
    # Service Interest
    interested_services = models.TextField(help_text="Describe what errand services they're interested in")
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    urgency = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')
    
    # Conversion
    converted_to_customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='original_lead')
    conversion_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_leads')
    
    # Notes
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['source']),
            models.Index(fields=['assigned_employee']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        if self.company_name:
            return f"{self.company_name} - {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def convert_to_customer(self, user=None):
        """Convert this lead to a customer"""
        if self.converted_to_customer:
            return self.converted_to_customer
        
        customer = Customer.objects.create(
            first_name=self.first_name,
            last_name=self.last_name,
            company_name=self.company_name,
            email=self.email,
            phone=self.phone or '',
            address_line1='',  # Will need to be filled later
            city='',
            state='',
            postal_code='',
            assigned_employee=self.assigned_employee,
            created_by=user,
        )
        
        self.converted_to_customer = customer
        self.conversion_date = timezone.now()
        self.status = 'won'
        self.save()
        
        return customer


class CustomerNote(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_important = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.customer} - {self.created_at.strftime('%Y-%m-%d')}"


class LeadNote(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='lead_notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_important = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.lead} - {self.created_at.strftime('%Y-%m-%d')}"
