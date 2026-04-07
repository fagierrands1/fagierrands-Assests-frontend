from django.contrib import admin
from .models import (ServiceCategory, Service, ServiceRequest, ServiceRequestUpdate, 
                     ServiceQuote, ServiceQuoteItem, ServiceFeedback)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'service_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    
    def service_count(self, obj):
        return obj.services.count()
    service_count.short_description = 'Services Count'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'pricing_type', 'base_price', 'estimated_duration_minutes', 'is_active']
    list_filter = ['category', 'pricing_type', 'is_active', 'requires_approval']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'base_price']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing', {
            'fields': ('pricing_type', 'base_price', 'hourly_rate')
        }),
        ('Service Details', {
            'fields': ('estimated_duration_minutes', 'requires_approval', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    readonly_fields = ['created_at', 'updated_at']


class ServiceRequestUpdateInline(admin.TabularInline):
    model = ServiceRequestUpdate
    extra = 1
    fields = ['update_text', 'status_changed_to', 'progress_percentage', 'created_by']
    readonly_fields = ['created_by']


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['request_id', 'title', 'customer', 'service', 'status', 'priority', 'assigned_employee', 'total_amount', 'requested_date']
    list_filter = ['status', 'priority', 'service__category', 'assigned_employee', 'created_at']
    search_fields = ['request_id', 'title', 'customer__first_name', 'customer__last_name', 'description']
    list_editable = ['status', 'assigned_employee', 'priority']
    readonly_fields = ['request_id', 'total_amount', 'created_at', 'updated_at', 'created_by', 'is_overdue']
    date_hierarchy = 'requested_date'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_id', 'customer', 'service', 'title', 'description')
        }),
        ('Request Details', {
            'fields': ('special_instructions', 'priority', 'service_address')
        }),
        ('Scheduling', {
            'fields': ('requested_date', 'scheduled_date', 'completed_date')
        }),
        ('Assignment', {
            'fields': ('assigned_employee',)
        }),
        ('Status and Progress', {
            'fields': ('status', 'progress_percentage', 'is_overdue')
        }),
        ('Pricing', {
            'fields': ('quoted_amount', 'actual_hours', 'additional_charges', 'total_amount')
        }),
        ('Customer Feedback', {
            'fields': ('customer_rating', 'customer_feedback')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ['collapse']
        })
    )
    
    inlines = [ServiceRequestUpdateInline]
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class ServiceQuoteItemInline(admin.TabularInline):
    model = ServiceQuoteItem
    extra = 1
    fields = ['service', 'description', 'quantity', 'unit_price', 'total_price']
    readonly_fields = ['total_price']


@admin.register(ServiceQuote)
class ServiceQuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_id', 'customer', 'title', 'status', 'total_amount', 'valid_until', 'created_at']
    list_filter = ['status', 'created_at', 'valid_until']
    search_fields = ['quote_id', 'customer__first_name', 'customer__last_name', 'title']
    list_editable = ['status']
    readonly_fields = ['quote_id', 'total_amount', 'created_at', 'updated_at', 'created_by', 'is_expired']
    
    fieldsets = (
        ('Quote Information', {
            'fields': ('quote_id', 'customer', 'service_request', 'title', 'description')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Validity', {
            'fields': ('valid_until', 'status', 'is_expired')
        }),
        ('Terms', {
            'fields': ('terms_and_conditions', 'notes')
        }),
        ('Response Tracking', {
            'fields': ('sent_date', 'responded_date'),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ['collapse']
        })
    )
    
    inlines = [ServiceQuoteItemInline]
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ServiceFeedback)
class ServiceFeedbackAdmin(admin.ModelAdmin):
    list_display = ['service_request', 'overall_satisfaction', 'average_rating', 'would_recommend', 'would_use_again', 'created_at']
    list_filter = ['overall_satisfaction', 'would_recommend', 'would_use_again', 'created_at']
    search_fields = ['service_request__request_id', 'service_request__customer__first_name', 'service_request__customer__last_name']
    readonly_fields = ['average_rating', 'created_at']
    
    fieldsets = (
        ('Service Request', {
            'fields': ('service_request',)
        }),
        ('Ratings', {
            'fields': ('overall_satisfaction', 'service_quality', 'timeliness', 'communication', 'value_for_money', 'average_rating')
        }),
        ('Feedback', {
            'fields': ('positive_feedback', 'improvement_suggestions', 'would_recommend', 'would_use_again')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ['collapse']
        })
    )
